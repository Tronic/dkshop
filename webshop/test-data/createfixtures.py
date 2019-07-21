import datetime
import json
import random
import re
import pandas
from webshop.slugs import USlug

slugs = set()
slugnum = 1

def slugify(s):
    global slugs, slugnum
    # Replace spaces with underscores, remove invalid characters, limit length
    s = str(s).replace(" ", "_")
    s = re.sub("[^-a-zA-Z0-9_]", "", s)[:30]
    # If malformed or not unique, assign numbered slug instead
    if not re.match(USlug.regex, s) or s in slugs:
        s = f"Slug-{slugnum}"
        slugnum += 1
    slugs.add(s)
    return s

def do_genres(min_number=100):
    global genrepks
    genrepks = {}
    # Split up and read all genres
    genres = {}
    for l in [s.split("/") for s in df["Genre"].values]:
        for g in l:
            slug = g.lower().replace(" ", "_")
            if slug in genres:
                genres[slug][1] += 1
            else:
                genres[slug] = [g, 0]
    # Insert the genres with most games in them to database
    db_genres = []
    pk = 1
    db_genres.append(dict(model="webshop.genre", pk=pk, fields=dict(
        slug="aalto", name="Aalto University", description="Educational game projects and test games.")
    ))
    for slug, (name, c) in genres.items():
        if c < min_number: continue
        pk += 1
        db_genres.append(dict(model="webshop.genre", pk=pk, fields=dict(
            slug=slug, name=name, description=f"{c} games known in this genre.")
        ))
    for g in db_genres: genrepks[g["fields"]["name"]] = g["pk"]
    return db_genres

def do_developers():
    global devpks
    devpks = {}
    # Find and add unique publishers and their associated users
    user_pk, dev_pk = 1000, 1000
    developers = []
    devnames = {str(name) for name in df["Publisher"].values}
    for name in devnames:
        slug = slugify(name)
        user = dict(model="auth.user", pk=user_pk, fields=dict(
            username=f"devuser-{dev_pk}"
        ))
        dev = dict(model="webshop.developer", pk=dev_pk, fields=dict(
            user=user_pk, slug=slug, name=name, registered="2019-01-01"
        ))
        devpks[name] = dev_pk
        user_pk += 1
        dev_pk += 1
        developers += user, dev
    return developers

def do_games():
    games = []
    pk = 1000
    # Add games to publishers
    for r in range(len(df)):
        g = df.iloc[r]
        name = g["Title"]
        slug = slugify(name)
        m, d, y = [int(v) for v in df["Release Date"].values[0].split("/")]
        date = datetime.date(y, m, d)
        popularity = round(10.0*g["User Rating"], 1)
        if not popularity > 0.0: popularity = 0.0
        game = dict(model="webshop.game", pk=pk, fields=dict(
            slug=slug, name=name, published=str(date), popularity=popularity,
            url="http://google.com/",
            price = "0.00" if "Free to Play" in g["Genre"] else "10.00",
            developer=devpks[str(g["Publisher"])],
            genres=[pk for name, pk in genrepks.items() if name in g["Genre"]],
        ))
        games.append(game)
        pk += 1
    return games

def do_aalto():
    return [
        dict(model="auth.user", pk=100, fields=dict(username="aaltodev")),
        dict(model="auth.user", pk=101, fields=dict(username="aaltouser")),
        dict(model="webshop.developer", pk=100, fields=dict(
            user=100, slug="WSD", name="Web Software Development",
            registered="2019-02-01",
        )),
        dict(model="webshop.game", pk=100, fields=dict(
            developer=100,
            slug="TestGame", name="Stonebag", url="/s/test-game/Test%20Game.htm",
            description="You collect stones into your backbag.\n\nThe coolest RPG ever!",
            genres=(1, 11, 14),
            image="games/img-100.png",
            published="2019-02-01",
        )),
        dict(model="webshop.game", pk=101, fields=dict(
            developer=100,
            slug="SuperDeoxy", name="Super Deoxy", url="/s/deoxy-game/index.html",
            description="""GIANT OXYGEN RADICALS are taking over the atmosphere and the end is nigh. It is up to you to save the world! Only SUPER DEOXY may stop the climate change by jumping on the oxygen, or at least deter the inevitable until the end...

Use arrow keys to move and jump.

This game has been implemented as a part of the project work for the WSD course at Aalto University.""",
            genres=(1, 2),
            price="10.00",
            image="games/img-101.png",
            published="2018-01-01",
            users=(101,),
        )),
        dict(model="webshop.game", pk=102, fields=dict(
            developer=100,
            slug="RecursionGame", name="Recursion Game", url=".",
            description="Must go in DEEPER!",
            genres=(1, 9),
            price="10.00",
            published="2008-01-01",
        )),
        dict(model="webshop.sale", pk=100, fields=dict(
            developer=100,  # aaltodev
            buyer=101,  # aaltouser
            game=101,  # Super Deoxy
            price="10.00",
            ref="aalto-fixture",
            date="2019-02-28",
        )),

    ]

def do_sales():
    ret = []
    sale_pk = 101
    random.seed(0)
    date = datetime.datetime.fromisoformat("2018-01-01")
    enddate = datetime.datetime.fromisoformat("2019-02-28")
    while date < enddate:
        ret.append(dict(model="webshop.sale", pk=sale_pk, fields=dict(
            developer=100, # aaltodev
            game=random.randint(101, 102),
            price="10.00",
            ref=f"sales-fixture-{sale_pk}",
            date=str(date),
        )))
        sale_pk += 1
        date += datetime.timedelta(seconds=random.randint(1, 80000))
    return ret

def main():
    global df
    df = pandas.read_csv("tableE.csv")
    json.dump(do_genres(), open("../fixtures/1-genres.json", "w"))
    gamedata = do_developers() + do_games()
    json.dump(do_aalto(), open("../fixtures/2-aalto.json", "w"))
    json.dump(gamedata, open("../fixtures/3-bulk.json", "w"))
    json.dump(do_sales(), open("../fixtures/4-sales.json", "w"))
if __name__ == "__main__": main()

