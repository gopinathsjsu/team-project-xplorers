// src/pages/AdminDashboard.jsx
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import RestaurantList from "../components/RestaurantList";
import { getAllAdminRestaurants } from "../api/auth";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [pending, setPending] = useState([]);
  const [approved, setApproved] = useState([]);
  const [error, setError] = useState(null);

  const fetchRestaurants = useCallback(async () => {
    try {
      const all = await getAllAdminRestaurants();
      setPending(all.filter(r => !r.is_approved));
      setApproved(all.filter(r => r.is_approved));
    } catch (e) {
      console.error("Failed to fetch restaurants:", e);
      setError("Could not load restaurants.");
    }
  }, []);

  useEffect(() => {
    fetchRestaurants();
  }, [fetchRestaurants]);

  if (error) {
    return (
      <>
        <Header />
        <div className="admin-dashboard-bg">
          <div className="admin-dashboard-overlay">
            <div className="admin-dashboard-content">
              <h1 className="textCenter">Admin Dashboard</h1>
              <p className="error">{error}</p>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="admin-dashboard-bg">
        <div className="admin-dashboard-overlay">
          <div className="admin-dashboard-content">
            <h1 className="textCenter">Admin Dashboard</h1>

            <section>
              <h2 className="textCenter">Pending Restaurants</h2>
              <RestaurantList
                restaurants={pending}
                isNavigationFromAdmin
                refreshData={fetchRestaurants}
              />
            </section>

            <section>
              <h2 className="textCenter">Approved Restaurants</h2>
              <RestaurantList
                restaurants={approved}
                isNavigationFromAdmin
                isRemoveRestaurant
                refreshData={fetchRestaurants}
              />
            </section>

            <div className="textCenter">
              <button
                className="analytics-button"
                onClick={() => navigate("/adminAnalytics")}
              >
                View Analytics
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
