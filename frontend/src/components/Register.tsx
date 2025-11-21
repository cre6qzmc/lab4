import React, { useState } from 'react';
import axios from 'axios';
import './Register.css';

interface RegisterProps {
  onSuccess: (userData: any) => void;
  onSwitchToLogin: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    login: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setMessage('');
    setError('');
    setValidationErrors([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage('');
    setError('');
    setValidationErrors([]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/register', formData);
      setMessage(response.data.message);
      
      // Немедленный переход
      onSuccess({
        login: formData.login,
        user_id: response.data.user_id
      });
      
    } catch (err: any) {
      if (err.response) {
        const errorDetail = err.response.data.detail;
        
        if (typeof errorDetail === 'string') {
          if (errorDetail.includes(';')) {
            setValidationErrors(errorDetail.split(';').map(e => e.trim()));
          } else if (errorDetail.includes('\n')) {
            setValidationErrors(errorDetail.split('\n').map(e => e.trim()).filter(e => e));
          } else {
            setError(errorDetail);
          }
        } else {
          setError('Registration failed: ' + JSON.stringify(errorDetail));
        }
      } else if (err.request) {
        setError('Network error: Cannot connect to server');
      } else {
        setError('Unexpected error: ' + err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Функция для проверки пароля в реальном времени
  const checkPasswordStrength = (password: string) => {
    const requirements = [
      { test: (p: string) => p.length >= 8, message: 'Длина пароля не менее 8 символов' },
      { test: (p: string) => /[A-Z]/.test(p), message: 'Минимум 1 буква в верхнем регистре (A-Z)' },
      { test: (p: string) => /[a-z]/.test(p), message: 'Минимум 1 буква в нижнем регистре (a-z)' },
      { test: (p: string) => /[0-9]/.test(p), message: 'Минимум 1 цифра (0-9)' },
      { test: (p: string) => /[!@#$%^&*(),.?":{}|<>]/.test(p), message: 'Минимум 1 спецсимвол (!@#$%^&*)' }
    ];

    return requirements.map(req => ({
      met: req.test(password),
      message: req.message
    }));
  };

  const passwordRequirements = checkPasswordStrength(formData.password);
  const allRequirementsMet = passwordRequirements.every(req => req.met);

  // Проверяем валидность логина
  const isLoginValid = formData.login.length >= 3 && 
                      formData.login.length <= 32 && 
                      /^[a-zA-Z0-9._-]+$/.test(formData.login);

  // Получаем класс для поля логина
  const getLoginClass = () => {
    if (!formData.login) return '';
    return isLoginValid ? 'valid' : 'invalid';
  };

  // Получаем класс для поля пароля
  const getPasswordClass = () => {
    if (!formData.password) return '';
    return allRequirementsMet ? 'valid' : 'invalid';
  };

  // Функция для определения состояния disabled кнопки
  const isButtonDisabled = (): boolean => {
    return isLoading || !formData.login || !formData.password || !allRequirementsMet || !isLoginValid;
  };

  return (
    <div className="register-container">
      <form onSubmit={handleSubmit} className="register-form">
        <h2>Страница регистрации</h2>
        
        <div className="form-group">
          <label htmlFor="login">Логин:</label>
          <input
            type="text"
            id="login"
            name="login"
            value={formData.login}
            onChange={handleChange}
            className={getLoginClass()}
            required
            minLength={3}
            maxLength={32}
            pattern="[a-zA-Z0-9._-]+"
            title="Login can only contain letters, numbers, ., _, -"
            disabled={isLoading}
          />
          <small className="input-hint">3-32 символа (A-Za-z), . _ -</small>
        </div>

        <div className="form-group">
          <label htmlFor="password">Пароль</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className={getPasswordClass()}
            required
            minLength={8}
            title="Password must meet all requirements below"
            disabled={isLoading}
          />
          
          {/* Индикатор силы пароля в реальном времени */}
          {formData.password && (
            <div className="password-strength">
              <h4>Сложность пароля:</h4>
              <div className="requirements-list">
                {passwordRequirements.map((req, index) => (
                  <div 
                    key={index} 
                    className={`requirement ${req.met ? 'met' : 'unmet'}`}
                  >
                    {req.message}
                  </div>
                ))}
              </div>
              {allRequirementsMet && (
                <div className="all-requirements-met">
                  Все требования к паролю выполнены!
                </div>
              )}
            </div>
          )}
        </div>

        <button 
          type="submit" 
          disabled={isButtonDisabled()}
        >
          {isLoading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>

        {message && (
          <div className="success-message">
            {message}
          </div>
        )}
        
        {/* Показываем детальные ошибки валидации */}
        {validationErrors.length > 0 && (
          <div className="validation-errors">
            <h4>Исправьте следующие ошибки:</h4>
            <ul>
              {validationErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}
        
        {error && !validationErrors.length && (
          <div className="error-message">{error}</div>
        )}

        <div className="switch-auth">
          <p>Уже есть аккаунт? <button type="button" onClick={onSwitchToLogin}>Вход</button></p>
        </div>

        <div className="password-requirements">
          <h4>Требования к паролю:</h4>
          <ul>
            <li>Длина пароля не менее 8 символов</li>
            <li>Минимум 1 буква в верхнем регистре (A-Z)</li>
            <li>Минимум 1 буква в нижнем регистре (a-z)</li>
            <li>Минимум 1 цифра (0-9)</li>
            <li>Минимум 1 спецсимвол (!@#$%^&*)</li>
          </ul>
        </div>
      </form>
    </div>
  );
};

export default Register;