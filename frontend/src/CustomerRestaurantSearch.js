// src/pages/CustomerRestaurantSearch.jsx
import React, { useEffect, useState, useMemo, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import Header from "../components/Header";
import { getAllRestaurantsForCustomers } from "../api/auth";

const TIME_OPTIONS = Array.from({ length: 48 }, (_, i) => {
  const hour = Math.floor(i / 2);
  const min = i % 2 === 0 ? "00" : "30";
  return `${String(hour).padStart(2, "0")}:${min}`;
});

function getNearbyTimes(timeStr) {
  const [h, m] = timeStr.split(":").map(Number);
  const base = new Date(0, 0, 0, h, m).getTime();
  return [-30, 0, 30].map((offset) => {
    const t = new Date(base + offset * 60000);
    return `${String(t.getHours()).padStart(2, "0")}:${String(
      t.getMinutes()
    ).padStart(2, "0")}`;
  });
}

export default function CustomerRestaurantSearch() {
  const navigate = useNavigate();

  const [filters, setFilters] = useState({
    date: "",
    time: "",
    people: "",
    location: "",
  });
  const [restaurants, setRestaurants] = useState([]);
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(null);

  // Fetch once on mount
  useEffect(() => {
    (async () => {
      try {
        const data = await getAllRestaurantsForCustomers();
        setRestaurants(data);
        setResults(data);
      } catch (e) {
        console.error(e);
        setError("Failed to load restaurants.");
      }
    })();
  }, []);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFilters((f) => ({ ...f, [name]: value }));
  }, []);

  const handleSearch = useCallback(() => {
    const { date, time, people, location } = filters;
    if (!date || !time) {
      alert("Please select a date and time.");
      return;
    }
    if (!people || Number(people) <= 0) {
      alert("Please enter a valid number of people.");
      return;
    }
    const now = new Date();
    const nearby = getNearbyTimes(time).map(
      (slot) => new Date(`${date}T${slot}`)
    );
    if (!nearby.some((dt) => dt > now)) {
      alert("Please select a future date/time.");
      return;
    }

    const filtered = restaurants.filter((r) => {
      const matchesLocation =
        !location ||
        r.city.toLowerCase().includes(location.toLowerCase()) ||
        r.state.toLowerCase().includes(location.toLowerCase()) ||
        (r.zip_code && r.zip_code.includes(location));
      const available =
        r.availability?.some((slot) => getNearbyTimes(time).includes(slot)) &&
        r.tables?.some((t) => t.is_active);
      return matchesLocation && available;
    });

    setResults(filtered);
    setHasSearched(true);
  }, [filters, restaurants]);

  const handleBooking = useCallback(
    (r, slot) => {
      const { restaurant_id } = r;
      const { date, people } = filters;
      navigate(
        `/book/${restaurant_id}?time=${slot}&date=${date}&people=${people}`
      );
    },
    [filters, navigate]
  );

  if (error) {
    return (
      <>
        <Header />
        <div className="customer-bg">
          <p className="error">{error}</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="customer-bg">
        <div className="customer-search-container">
          <h2>Find a Restaurant</h2>

          <FilterForm
            filters={filters}
            onChange={handleChange}
            onSearch={handleSearch}
          />

          <ResultsList
            results={results}
            hasSearched={hasSearched}
            time={filters.time}
            onBook={handleBooking}
          />
        </div>
      </div>
    </>
  );
}

function FilterForm({ filters, onChange, onSearch }) {
  return (
    <div className="filters">
      <input
        type="date"
        name="date"
        value={filters.date}
        onChange={onChange}
      />
      <select
        name="time"
        value={filters.time}
        onChange={onChange}
        className="filtersSelect"
      >
        <option value="">Select Time</option>
        {TIME_OPTIONS.map((t) => (
          <option key={t} value={t}>
            {t}
          </option>
        ))}
      </select>
      <input
        type="number"
        name="people"
        placeholder="# People"
        value={filters.people}
        onChange={onChange}
      />
      <input
        type="text"
        name="location"
        placeholder="City / State / Zip (optional)"
        value={filters.location}
        onChange={onChange}
      />
      <button onClick={onSearch}>Search</button>
    </div>
  );
}

function ResultsList({ results, hasSearched, time, onBook }) {
  if (results.length === 0) {
    return <p>No restaurants match your search.</p>;
  }

  const nearbySlots = time ? getNearbyTimes(time) : [];

  return (
    <div className="results">
      {results.map((r) => (
        <div key={r.restaurant_id} className="result-card">
          <h3>{r.name}</h3>
          <p>
            Cuisine: <strong>{r.cuisine_type}</strong> | Cost:{" "}
            <strong>{"$".repeat(r.cost_rating)}</strong>
          </p>
          <p>
            {r.avg_rating} ⭐ ({r.reviews.length} reviews) | Booked{" "}
            {r.times_booked_today} times today
          </p>
          <p>
            <Link
              to={`/read-review?restaurant_id=${r.restaurant_id}`}
              className="review-link"
            >
              📖 Read Reviews
            </Link>
          </p>
          <p>
            <Link
              to={`/restaurant-details?restaurant_id=${r.restaurant_id}`}
              className="review-link"
            >
              📖 Details
            </Link>
          </p>

          {hasSearched && (
            <div className="slots">
              {r.availability
                ?.filter(
                  (slot) =>
                    nearbySlots.includes(slot) &&
                    !r.booked_slots?.includes(slot)
                )
                .map((slot) => (
                  <button
                    key={slot}
                    onClick={() => onBook(r, slot)}
                    className="slot-btn"
                  >
                    {slot}
                  </button>
                ))}
              {r.availability?.filter(
                (slot) =>
                  nearbySlots.includes(slot) &&
                  !r.booked_slots?.includes(slot)
              ).length === 0 && (
                <p style={{ color: "#ccc", marginTop: 8 }}>
                  No available slots near this time.
                </p>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
