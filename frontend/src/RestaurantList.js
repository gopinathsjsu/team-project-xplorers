import React from 'react';
import { useNavigate } from 'react-router-dom';
import './styles.css';

const RestaurantList = ({ restaurants, isNavigationFromAdmin, isRemoveRestaurant }) => {
  const navigate = useNavigate();

  const handleUpdateClick = (restaurantId) => {
    navigate(`/update/${restaurantId}`);
  };

  const handleApproveClick = (restaurantId) => {
    alert(`Approved restaurant ID: ${restaurantId}`);
  };

  const handleRemoveClick = (restaurantId) => {
    alert(`Removed restaurant ID: ${restaurantId}`);
  };

  return (
    <div className="list-container">
      <h2 className="page-title">
        {isNavigationFromAdmin
          ? isRemoveRestaurant
            ? '🗑️ Remove Restaurants'
            : '🛠️ Approve Restaurants'
          : '🍽️ Restaurant Directory'}
      </h2>
      <div className="card-grid">
        {restaurants.map((restaurant) => (
          <div key={restaurant.restaurant_id} className="restaurant-card">
            <h3 className="restaurant-name">{restaurant.name}</h3>
            <p className="description">{restaurant.description}</p>
            <p className="location">{restaurant.city}, {restaurant.state}</p>
            <p className="contact">{restaurant.email} | {restaurant.phone_number}</p>

            {isNavigationFromAdmin ? (
              isRemoveRestaurant ? (
                <button
                  className="remove-button"
                  onClick={() => handleRemoveClick(restaurant.restaurant_id)}
                >
                  ❌ Remove Restaurant
                </button>
              ) : (
                <button
                  className="approve-button"
                  onClick={() => handleApproveClick(restaurant.restaurant_id)}
                >
                  ✅ Approve
                </button>
              )
            ) : (
              <button
                className="update-button"
                onClick={() => handleUpdateClick(restaurant.restaurant_id)}
              >
                ✏️ Update
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default RestaurantList;
