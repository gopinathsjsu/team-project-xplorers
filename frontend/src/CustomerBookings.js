// src/pages/CustomerBookings.jsx
import React, { useEffect, useState, useCallback } from "react";
import Header from "../components/Header";
import {
  addReview,
  cancelCustomerBooking,
  getAllBookings,
} from "../api/auth";

export default function CustomerBookings() {
  const [reservations, setReservations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);

  const fetchReservations = useCallback(async () => {
    try {
      const data = await getAllBookings();
      setReservations(data);
    } catch (e) {
      console.error("Error fetching bookings:", e);
      setError("Failed to load bookings.");
    }
  }, []);

  useEffect(() => {
    fetchReservations();
  }, [fetchReservations]);

  const handleReviewSubmit = async () => {
    try {
      await addReview({
        restaurant_id: selected.restaurant_id,
        rating: Number(rating),
        comment: comment.trim(),
      });
      alert("Review submitted!");
      setSelected(null);
      setComment("");
      setRating(5);
    } catch (e) {
      console.error("Error submitting review:", e);
      alert("Failed to submit review.");
    }
  };

  const handleCancel = async (id) => {
    try {
      await cancelCustomerBooking({ reservation_id: id });
      alert("Booking canceled");
      fetchReservations();
    } catch (e) {
      console.error("Error cancelling booking:", e);
      alert("Failed to cancel.");
    }
  };

  if (error) {
    return (
      <>
        <Header />
        <div className="customer-bookings">
          <p className="error">{error}</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="customer-bookings">
        <h2>My Bookings</h2>
        {reservations.length === 0 ? (
          <p>No reservations found.</p>
        ) : (
          reservations.map((res) => (
            <ReservationCard
              key={res.reservation_id}
              reservation={res}
              onReview={() => setSelected(res)}
              onCancel={() => handleCancel(res.reservation_id)}
            />
          ))
        )}

        {selected && (
          <ReviewModal
            reservation={selected}
            rating={rating}
            comment={comment}
            onRatingChange={setRating}
            onCommentChange={setComment}
            onSubmit={handleReviewSubmit}
            onClose={() => setSelected(null)}
          />
        )}
      </div>
    </>
  );
}

function ReservationCard({ reservation, onReview, onCancel }) {
  const {
    reservation_id,
    restaurant_name,
    party_size,
    reservation_time,
    status,
    table_id,
    confirmation_code,
    special_requests,
  } = reservation;
  const isCompleted = status.toLowerCase() === "completed";
  const isConfirmed = status.toLowerCase() === "confirmed";

  return (
    <div className="result-card">
      <h3>Reservation #{reservation_id}</h3>
      <p><strong>Restaurant:</strong> {restaurant_name}</p>
      <p><strong>Party Size:</strong> {party_size}</p>
      <p>
        <strong>Time:</strong>{" "}
        {new Date(reservation_time).toLocaleString()}
      </p>
      <p><strong>Status:</strong> {status}</p>
      <p><strong>Table ID:</strong> {table_id}</p>
      <p><strong>Confirmation Code:</strong> {confirmation_code}</p>
      {special_requests && (
        <p><strong>Special Requests:</strong> {special_requests}</p>
      )}
      {isCompleted && (
        <button className="review-button" onClick={onReview}>
          Leave a Review
        </button>
      )}
      {isConfirmed && (
        <button className="cancel-button" onClick={onCancel}>
          Cancel Booking
        </button>
      )}
    </div>
  );
}

function ReviewModal({
  reservation,
  rating,
  comment,
  onRatingChange,
  onCommentChange,
  onSubmit,
  onClose,
}) {
  return (
    <div className="review-modal">
      <h3>Review for Reservation #{reservation.reservation_id}</h3>
      <label>
        Rating:
        <select
          value={rating}
          onChange={(e) => onRatingChange(e.target.value)}
          className="review-rating-select"
        >
          {[5, 4, 3, 2, 1].map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </label>
      <textarea
        rows={4}
        placeholder="Write your review..."
        value={comment}
        onChange={(e) => onCommentChange(e.target.value)}
        className="special-request-textarea"
      />
      <div className="modal-buttons">
        <button onClick={onSubmit} className="submit-review-btn">
          Submit Review
        </button>
        <button onClick={onClose} className="cancel-review-btn">
          Cancel
        </button>
      </div>
    </div>
  );
}
