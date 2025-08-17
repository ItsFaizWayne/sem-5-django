# rentals/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from games.models import Game
from .models import Rental
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponseForbidden


@login_required
def request_rental(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if not game.available:
        messages.error(request, "This game is currently not available.")
        return redirect('game_list')

    # Check if already requested
    if Rental.objects.filter(user=request.user, game=game, status='pending').exists():
        messages.warning(request, "You have already requested this game.")
        return redirect('game_list')

    Rental.objects.create(user=request.user, game=game)
    messages.success(request, f"Rental request for {game.title} submitted!")
    return redirect('game_list')



@login_required
def my_rentals(request):
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'rentals/my_rentals.html', {'rentals': rentals})


@login_required
def update_rental_status(request, rental_id, new_status):  # <- accept new_status
    rental = get_object_or_404(Rental, id=rental_id)

    # Optional: restrict student admins to only their own rentals
    if not request.user.is_superuser and rental.game.added_by != request.user:
        messages.error(request, "You don't have permission to update this rental.")
        return redirect('student_admin_dashboard')

    rental.status = new_status.lower()
    if new_status.lower() == 'approved':
        rental.approved_at = timezone.now()
    rental.save()
    messages.success(request, f"Rental status updated to {new_status}.")
    
    # Redirect to appropriate dashboard
    if request.user.is_superuser:
        return redirect('superadmin_dashboard')
    else:
        return redirect('student_admin_dashboard')

# from django.shortcuts import redirect, get_object_or_404
# from .models import Rental

# def approve_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id)
#     rental.status = "Approved"
#     rental.save()
#     return redirect('super_admin_dashboard')

# def reject_rental(request, rental_id):
#     rental = get_object_or_404(Rental, id=rental_id)
#     rental.status = "Rejected"
#     rental.save()
#     return redirect('super_admin_dashboard')
