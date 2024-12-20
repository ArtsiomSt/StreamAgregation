import React, {useState} from 'react';
import {useNavigate} from "react-router-dom";
import NavBar from "./navbar"
import "../styles/login.css"


const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [detail, setDetail] = useState('');

    const navigate = useNavigate();

    const handleRegisterRedirect = async () => {
        navigate('/register')
    }
    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "email": email,
                    "password": password
                })
            });

            if (response.status === 200) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                document.cookie = "email="+email+"samesite=strict"+"max-age="+24*3600
                const a = localStorage.getItem("access_token");
                navigate('/profile')
            } else {
                const data = await response.json();
                console.log(data.detail)
                setDetail(data.detail)
            }
        } catch (error) {
            console.error('An error occurred', error);
        }
    };
    return (
        <div>
            <NavBar/>
            <form onSubmit={handleLogin} className="login-form">
                <div className="input-field">
                    <label className="input-label">Email: </label>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required={true}
                        className="input-input"
                    />
                </div>

                <div className="input-field">
                    <label className={"input-label"}>Password: </label>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required={true}
                        className="input-input"
                    />
                </div>

                <button type="submit" className={"input-button"}>Login</button>
                <h3>{detail}</h3>
                <div>
                    <h6>Don't have account? <button onClick={handleRegisterRedirect} className={"input-button"}>Register</button></h6>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;