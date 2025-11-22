from django.core.mail import send_mail
from django.conf import settings


def send_order_emails(order):
    """
    Sends order confirmation to user and notification to admin(s).

    Args:
        order: Order instance
    """
    # Subject and messages
    subject_user = f"Commande #{order.order_number} passée"
    message_user = (
        f"Bonjour {order.user.first_name},\n\n"
        f"Confirmation de commande #{order.order_number} : Votre commande a été enregistrée avec succès. "
        f"Un email de confirmation contenant votre facture et les détails de votre commande vous sera envoyé à l'adresse {order.email}. "
        f"Merci pour votre confiance !"
        f"Montant total: {order.total_amount}.\n"
    )

    subject_admin = f"Nouvelle commande #{order.order_number}"
    message_admin = (
        f"Nouvelle commande #{order.order_number} passée par "
        f"({order.user.email}).\n"
        f"Montant total: {order.total_amount}.\n"
    )

    # Send to user
    send_mail(
        subject_user,
        message_user,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        fail_silently=False,
    )

    # Send to admin(s)
    send_mail(
        subject_admin,
        message_admin,
        settings.DEFAULT_FROM_EMAIL,
        [admin_email for _, admin_email in settings.ADMINS],
        fail_silently=False,
    )
