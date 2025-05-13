import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { bookReservation, getAllRestaurantsForCustomers } from "./api/auth";

/**
 * Ensures time format has seconds
 * @param {string} timestamp - Time in format "YYYY-MM-DD HH:mm" or "YYYY-MM-DD HH:mm:ss"
 * @returns {string} - Time with seconds
 */
const ensureSeconds = (timestamp) => {
  return /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(timestamp)
    ? `${timestamp}:00`
    : timestamp;
};

/**
 * Converts date and time string to ISO format with Z
 * @param {string} str - Date and time string
 * @returns {string} - ISO formatted string
 */
const toIsoZ = (str) => {
  return `${str.trim().replace(" ", "T")}Z`;
};

const BookRestaurant = () => {
  // State management
  const [specialRequest, setSpecialRequest] = useState("");
  const [restaurant, setRestaurant] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Router hooks
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // URL parameters
  const people = searchParams.get("people");
  const time = searchParams.get("time");
  const date = searchParams.get("date");

  useEffect(() => {
    const fetchRestaurant = async () => {
      try {
        setIsLoading(true);
        const data = await getAllRestaurantsForCustomers();
        const foundRestaurant = data.find(r => r.restaurant_id === parseInt(id));
        
        if (!foundRestaurant) {
          setError("Restaurant not found");
        } else {
          setRestaurant(foundRestaurant);
        }
      } catch (error) {
        console.error("Failed to fetch restaurant:", error);
        setError("Failed to load restaurant data");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchRestaurant();
  }, [id]);

  const handleBook = async () => {
    try {
      const dateAndTime = ensureSeconds(`${date} ${time}`);
      const availableTable = restaurant.tables.find(
        table => table.capacity >= parseInt(people) && table.is_active === true
      );
      
      if (!availableTable) {
        throw new Error("No suitable table available for your party size");
      }
      
      await bookReservation({
        restaurant_id: restaurant.restaurant_id,
        table_id: availableTable.table_id,
        reservation_time: toIsoZ(dateAndTime),
        party_size: parseInt(people),
        special_requests: specialRequest,
      });
      
      alert(`✅ Table booked at ${restaurant.name} for ${time}. Confirmation sent!`);
      navigate("/my-bookings");
    } catch (err) {
      console.error("Error booking reservation:", err);
      alert(`Failed to book: ${err.message || "Unknown error"}`);
    }
  };

  const handleCancel = () => {
    navigate("/custDashboard");
  };

  if (isLoading) return <div className="loading">Loading restaurant information...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!restaurant) return <div className="not-found">Restaurant not found.</div>;

  const reviewsCount = restaurant.reviews?.length || 0;
  const googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(restaurant.name+'+'+restaurant.city)}`;

  return (
    <div className="book-bg">
      <div className="booking-container">
        <h2>Booking at {restaurant.name}</h2>
        
        <div className="booking-details">
          <p><strong>Time:</strong> {time}</p>
          <p><strong>Date:</strong> {date}</p>
          <p><strong>Party Size:</strong> {people}</p>
          <p><strong>Cuisine:</strong> {restaurant.cuisine_type}</p>
          <p><strong>Rating:</strong> {restaurant.avg_rating} ⭐ ({reviewsCount} reviews)</p>
        </div>

        <section className="location-section">
          <h4>📍 Location</h4>
          <a
            href={googleMapsUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            View on Google Maps
          </a>
        </section>

        <section className="special-requests-section">
          <h4>📝 Special Requests</h4>
          <textarea
            className="special-request-textarea"
            value={specialRequest}
            onChange={(e) => setSpecialRequest(e.target.value)}
            placeholder="E.g. Table near the window, vegetarian meal..."
            rows={4}
          />
        </section>

        <section className="actions-section">
          <h4>🪑 Booking Actions</h4>
          <div className="button-group">
            <button className="book-button" onClick={handleBook}>Book Table</button>
            <button className="cancel-button" onClick={handleCancel}>Discard Booking</button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default BookRestaurant;