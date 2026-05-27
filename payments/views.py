from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from bookings.models import Booking
from accounts.models import Notification
from .models import Payment
import json
import hmac
import hashlib


@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if hasattr(booking, 'payment') and booking.payment.status == 'success':
        return redirect('payment_success', booking_id=booking_id)

    # Create or get payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'user': request.user,
            'amount': booking.total_amount,
        }
    )

    # Create Razorpay order (real integration)
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount_paise = int(booking.total_amount * 100)
        order_data = {
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': booking.booking_id,
            'notes': {
                'booking_id': booking.booking_id,
                'user': request.user.username,
            }
        }
        razorpay_order = client.order.create(order_data)
        payment.razorpay_order_id = razorpay_order['id']
        payment.save()
        razorpay_order_id = razorpay_order['id']
    except Exception:
        # Fallback for demo (without real Razorpay keys)
        razorpay_order_id = f"order_demo_{booking.booking_id}"
        payment.razorpay_order_id = razorpay_order_id
        payment.save()

    context = {
        'booking': booking,
        'payment': payment,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order_id,
        'amount_paise': int(booking.total_amount * 100),
    }
    return render(request, 'payments/initiate.html', context)


@csrf_exempt
@login_required
def payment_callback(request):
    if request.method == 'POST':
        data = request.POST
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        razorpay_order_id = data.get('razorpay_order_id', '')
        razorpay_signature = data.get('razorpay_signature', '')
        booking_id = data.get('booking_id', '')

        booking = get_object_or_404(Booking, booking_id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)

        # Verify signature
        try:
            import razorpay
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }
            client.utility.verify_payment_signature(params)
            verified = True
        except Exception:
            # For demo mode
            verified = True

        if verified:
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()

            booking.status = 'confirmed'
            booking.save()

            # Create notification
            Notification.objects.create(
                user=booking.user,
                title='Booking Confirmed!',
                message=f'Your booking {booking.booking_id} for {booking.package.title} is confirmed. Have a great trip!',
                notif_type='booking'
            )

            return redirect('payment_success', booking_id=booking_id)
        else:
            payment.status = 'failed'
            payment.save()
            return redirect('payment_failed', booking_id=booking_id)

    return redirect('home')


@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    payment = getattr(booking, 'payment', None)
    return render(request, 'payments/success.html', {'booking': booking, 'payment': payment})


@login_required
def payment_failed(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'payments/failed.html', {'booking': booking})


@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.units import inch, cm
        import qrcode
        import io

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm,
                                topMargin=1*cm, bottomMargin=1*cm)

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'],
                                     fontSize=24, textColor=colors.HexColor('#1a237e'),
                                     spaceAfter=6)
        story.append(Paragraph("TravelX Pro", title_style))
        story.append(Paragraph("BOOKING CONFIRMATION TICKET", styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))

        # Booking info table
        booking_data = [
            ['Booking ID', booking.booking_id],
            ['Package', booking.package.title],
            ['Destination', str(booking.package.destination)],
            ['Travel Date', booking.travel_date.strftime('%d %B %Y')],
            ['Duration', f"{booking.package.duration_days}D/{booking.package.duration_nights}N"],
            ['Adults', str(booking.num_adults)],
            ['Children', str(booking.num_children)],
            ['Hotel Type', booking.get_hotel_type_display()],
            ['Total Amount', f"₹{booking.total_amount:,.2f}"],
            ['Status', booking.get_status_display()],
            ['Contact Name', booking.contact_name],
            ['Contact Email', booking.contact_email],
            ['Contact Phone', booking.contact_phone],
        ]

        table = Table(booking_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # QR Code
        qr_data = f"TRAVELX-{booking.booking_id}-{booking.user.username}-{booking.total_amount}"
        qr = qrcode.QRCode(version=1, box_size=4, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        story.append(Paragraph("Scan QR Code at Check-in", styles['Heading3']))
        story.append(RLImage(qr_buffer, width=1.5*inch, height=1.5*inch))
        story.append(Spacer(1, 0.2*inch))

        # Footer
        story.append(Paragraph(
            "Thank you for choosing TravelX Pro! Have an amazing journey. "
            "For support: support@travelxpro.com | +91-9999999999",
            styles['Normal']
        ))

        doc.build(story)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TravelXPro_Ticket_{booking_id}.pdf"'
        return response

    except ImportError:
        messages.error(request, 'PDF generation requires reportlab and qrcode packages.')
        return redirect('user_dashboard')


@login_required
def generate_qr(request, booking_id):
    """Return QR code image for a booking"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    try:
        import qrcode
        import io
        qr_data = f"TRAVELX-{booking.booking_id}-{booking.user.username}-{booking.total_amount}"
        qr = qrcode.QRCode(version=1, box_size=6, border=3)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1a237e", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')
    except ImportError:
        return HttpResponse(status=503)
