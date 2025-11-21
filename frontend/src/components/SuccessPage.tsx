import React, { useState, useEffect } from 'react';
import './SuccessPage.css';

interface SuccessPageProps {
  userData: any;
  onLogout: () => void;
}

const SuccessPage: React.FC<SuccessPageProps> = ({ userData, onLogout }) => {
  const [currentKitten, setCurrentKitten] = useState(0);
  
  const kittenImages = [
    '/images/fenya1.jpg',
    '/images/fenya2.jpg',
    '/images/fenya3.jpg',
    '/images/fenya4.jpg',
    '/images/fenya5.jpg'
  ];

  const nextKitten = () => {
    setCurrentKitten((prev) => (prev + 1) % kittenImages.length);
  };

  // Автоматическая смена котиков каждые 5 секунд
  useEffect(() => {
    const interval = setInterval(nextKitten, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="success-container">
      <div className="success-content">
        <h1>Добро пожаловать, {userData.login}!</h1>
        <p>Вы успешно вошли в систему!</p>
        <p>Ваш ID: <strong>{userData.user_id}</strong></p>
        
        <div className="kitten-section">
          <h2>Посмотрите на фото Фени</h2>
          <img 
            src={kittenImages[currentKitten]} 
            alt="Cute kitten" 
            className="kitten-image"
          />
          <button onClick={nextKitten} className="refresh-btn">
            Следующий Феня
          </button>
        </div>

        <button onClick={onLogout} className="logout-btn">
          Выйти из системы
        </button>
      </div>
    </div>
  );
};

export default SuccessPage;