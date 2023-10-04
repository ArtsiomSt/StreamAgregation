import React, { useState } from 'react';
import {useNavigate} from "react-router-dom";


const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [detail, setDetail] = useState('');

    const navigate = useNavigate();
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

            if (response.status === 200){
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('refresh_token', data.refresh_token);
                const a = localStorage.getItem("access_token");
                navigate('/profile')
            }
            else {
                const data = await response.json();
                console.log(data.detail)
                setDetail(data.detail)
            }
        }
        catch (error){
            console.error('An error occurred', error);
        }
    };
   return (
        <form onSubmit={handleLogin}>
            <div>
                <label>Email: </label>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required={true}
                />
            </div>
            <div>
                <label>Password: </label>
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required={true}
                />
            </div>
      <button type="submit">login</button>
      <h3>{detail}</h3>
    </form>
  );
};

export default LoginForm;