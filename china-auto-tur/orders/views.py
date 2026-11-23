from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pages.models import ContactMessage


@require_POST
def quick_request(request):
    # заявка из модалки: без машины, менеджер подберёт сам по комментарию
    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    brand = request.POST.get("brand", "").strip()
    comment = request.POST.get("comment", "").strip()
    consent = request.POST.get("consent")

    digits = "".join(ch for ch in phone if ch.isdigit())
    if not name:
        return JsonResponse(
            {"ok": False, "error": "Напишите, как к вам обращаться"}, status=400
        )
    if len(digits) != 11 or digits[0] not in "78":
        return JsonResponse(
            {"ok": False, "error": "Телефон в формате +7 и десять цифр"}, status=400
        )
    if not consent:
        return JsonResponse(
            {"ok": False, "error": "Нужно согласие на обработку данных"}, status=400
        )

    ContactMessage.objects.create(
        kind="request",
        name=name,
        phone=phone,
        message=f'Марка: {brand or "не указана"}. {comment}',
    )
    return JsonResponse({"ok": True})


from django.http import JsonResponse
from django.views.decorators.http import require_POST

from pages.models import ContactMessage


@require_POST
def quick_request(request):
    # заявка из модалки: без машины, менеджер подберёт сам по комментарию
    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    brand = request.POST.get("brand", "").strip()
    comment = request.POST.get("comment", "").strip()
    consent = request.POST.get("consent")

    digits = "".join(ch for ch in phone if ch.isdigit())
    if not name:
        return JsonResponse(
            {"ok": False, "error": "Напишите, как к вам обращаться"}, status=400
        )
    if len(digits) != 11 or digits[0] not in "78":
        return JsonResponse(
            {"ok": False, "error": "Телефон в формате +7 и десять цифр"}, status=400
        )
    if not consent:
        return JsonResponse(
            {"ok": False, "error": "Нужно согласие на обработку данных"}, status=400
        )

    ContactMessage.objects.create(
        kind="request",
        name=name,
        phone=phone,
        message=f'Марка: {brand or "не указана"}. {comment}',
    )
    return JsonResponse({"ok": True})
