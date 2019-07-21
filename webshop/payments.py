from dkproject import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import get_object_or_404, Http404
from html5tagger import E
from datetime import datetime, timedelta
from . import layout, models
import hashlib

def digest(**keys):
    """Build MD5 checksum for the payment API (FIXME: non-b0rked hash function)."""
    keys["token"] = settings.PAYMENTS_SECRET
    checksumstr = "&".join(f"{key}={value}" for key, value in keys.items())
    return hashlib.md5(checksumstr.encode()).hexdigest()

@csrf_exempt  # Note: session/user is not used; the payment contains user info
def payment(request):
    """Handler for users returning from the payment system."""
    try:
        # Support either POST or GET from payment service
        args = request.POST if request.method == "POST" else request.GET
        pid, ref, result, checksum = args['pid'], args['ref'], args['result'], args['checksum']
    except ValueError:
        raise Http404("Malformed payment request")
    if checksum != digest(pid=pid, ref=ref, result=result):
        messages.error(request, "Payment verification failed!")
        return HttpResponseRedirect(reverse("webshop:index"))
    payment = get_object_or_404(models.Payment, pid=pid)
    user, game, price = payment.user, payment.game, payment.price
    if result == "success":
        game.purchase(user, price, ref)
        messages.success(request, "You have just purchased yourself " + game.name + "!")
    else:
        messages.warning(request, "No payment done.")
    payment.delete()
    return HttpResponseRedirect(game.get_absolute_url())

def purchase_form(request, game):
    """Construct a payment button/form to be included on the game's page."""
    # Prune old payments (TODO: bookkeeping could be done externally)
    models.Payment.objects.filter(date__lt=datetime.now()-timedelta(hours=1)).delete()
    assert request.user.is_authenticated
    assert game.price > 0
    payment = models.Payment(user=request.user, game=game, price=game.price)
    payment.save()
    url = request.build_absolute_uri(reverse("webshop:payment"))
    amount = str(payment.price)  # String rather than float is proper for Decimals
    pid = payment.pid.hex
    sid = settings.PAYMENTS_SID
    checksum = digest(pid=pid, sid=sid, amount=amount)
    if settings.PAYMENTS_GET:
        return HttpResponseRedirect(f"{settings.PAYMENTS_URL}?pid={pid}&sid={sid}&amount={amount}&success_url={url}&cancel_url={url}&error_url={url}&checksum={checksum}")
    # POST method via additional form
    with E.form(action=settings.PAYMENTS_URL, method="POST") as doc:
        doc.input(type="hidden", name="sid", value=sid)
        doc.input(type="hidden", name="pid", value=pid)
        doc.input(type="hidden", name="amount", value=amount)
        doc.input(type="hidden", name="checksum", value=checksum)
        doc.input(type="hidden", name="success_url", value=url)
        doc.input(type="hidden", name="cancel_url", value=url)
        doc.input(type="hidden", name="error_url", value=url)
        doc.input(type="submit", value="Simple Payments")
    # Alternative "payment method" in debug mode
    if settings.DEBUG:
        with doc.form(action=url, method="POST"):
            ref = f"steal-{pid}"
            result = "success"
            doc.input(type="hidden", name="pid", value=pid)
            doc.input(type="hidden", name="ref", value=ref)
            doc.input(type="hidden", name="result", value=result)
            doc.input(type="hidden", name="checksum", value=digest(pid=pid, ref=ref, result=result))
            doc.input(type="submit", value="Warez Pirate")
    return layout.page(request, "Choose payment provider", doc)
