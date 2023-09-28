import React, { useState } from 'react';
import {Navigate, useNavigate} from "react-router-dom";

const RegisterForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [username, setUsername] = useState('')
    const [lastName, setLastName] = useState('');
    const [detail, setDetail] = useState('');

    const navigate = useNavigate();
    const handleRegister = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    "email": email,
                    "password": password,
                    "username": username,
                    "first_name": firstName,
                    "last_name": lastName,
                })
            });

            if (response.status === 200){
                setDetail("Register Success");
                navigate("/login")
            }
            else {
                const data = await response.json();
                console.log(data.detail)
            }
        }
        catch (error){
            console.error('An error occurred', error);
        }
    };
    return (
        <form onSubmit={handleRegister}>
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
            <div>
                <label>Username: </label>
                <input
                    type="text"
                    placeholder="first name"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required={true}
                />
            </div>
            <div>
                <label>First Name: </label>
                <input
                    type="text"
                    placeholder="first name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                />
            </div>
            <div>
                <label>First Name: </label>
                <input
                    type="text"
                    placeholder="last name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                />
            </div>
      <button type="submit">Register</button>
      <h3>{detail}</h3>
    </form>
  );
};

export default RegisterForm;