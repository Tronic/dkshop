from django.test import TestCase
from collections import deque
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Developer, Game, Genre, submit_hiscore
import re

class LinkTest(TestCase):
    """Verify links within the site."""
    fixtures = "1-genres", "2-aalto", "4-sales",
    def test_links(self):
        """Breath-first travel all pages on the site"""
        path = "/"
        seen, queue = {path}, deque()
        queue.append(["Test start", path])
        while queue:
            parent, path = queue.popleft()
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, f"{parent} link to {path} is broken")
            content = response.content.decode()
            for link in re.findall('href="([^"]+)"', content):
                if link in seen: continue  # Avoid infinite loops
                seen.add(link)
                if link.startswith("/s/"): continue  # Skip static files
                if link.startswith("/m/"): continue  # Skip media files
                if link.startswith("/u/admin/"): continue  # Skip admin site
                queue.append([path, link])
        # All game pages visited?
        for g in Game.objects.all(): self.assertIn(g.get_absolute_url(), seen)
        for g in Genre.objects.all(): self.assertIn(g.get_absolute_url(), seen)
        for g in Developer.objects.all(): self.assertIn(g.get_absolute_url(), seen)

    def test_with_user(self):
        """Test all links via normal user account."""
        self.client.force_login(User.objects.get(username="aaltouser"))
        self.test_links()

    def test_with_dev(self):
        """Test all links via aaltodev account."""
        self.client.force_login(User.objects.get(username="aaltodev"))
        self.test_links()

    def test_with_super(self):
        """Test all links via superuser account."""
        self.client.force_login(User.objects.create_superuser("testsuper", email="", password="testsuper"))
        self.test_links()

class AddnTests(TestCase):
    fixtures = "1-genres", "2-aalto",
    def test_search(self):
        """Test the search for games"""
        response = self.client.get("/?q=Stone")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Stonebag")

    def test_hiscore(self):
        g = Game.objects.get(slug="TestGame")
        u = User.objects.get(username="aaltouser")
        submit_hiscore(g, u, 123.0)
        response = self.client.get(g.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "123")
