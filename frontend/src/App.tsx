import { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import SuccessPage from './components/SuccessPage';
import './App.css';

type AppState = 'register' | 'login' | 'success';

function App() {
  const [currentView, setCurrentView] = useState<AppState>('register');
  const [userData, setUserData] = useState<any>(null);

  console.log('App currentView:', currentView);
  console.log('App userData:', userData);

  const handleRegisterSuccess = (data: any) => {
    console.log('Register success with data:', data);
    setUserData(data);
    setCurrentView('success');
  };

  const handleLoginSuccess = (data: any) => {
    console.log('Login success with data:', data);
    setUserData(data);
    setCurrentView('success');
  };

  const handleLogout = () => {
    console.log('Logout clicked');
    setUserData(null);
    setCurrentView('login');
  };

  const handleSwitchToLogin = () => {
    console.log('Switching to login');
    setCurrentView('login');
  };

  const handleSwitchToRegister = () => {
    console.log('Switching to register');
    setCurrentView('register');
  };

  return (
    <div className="App">
      {currentView === 'register' && (
        <Register 
          onSuccess={handleRegisterSuccess} 
          onSwitchToLogin={handleSwitchToLogin}
        />
      )}
      {currentView === 'login' && (
        <Login 
          onSuccess={handleLoginSuccess}
          onSwitchToRegister={handleSwitchToRegister}
        />
      )}
      {currentView === 'success' && userData && (
        <SuccessPage 
          userData={userData} 
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;