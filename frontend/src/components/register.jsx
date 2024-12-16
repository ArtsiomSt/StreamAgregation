import React, {useState} from 'react';
import {useNavigate} from "react-router-dom";
import NavBar from "./navbar"
import "../styles/login.css"


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
            console.log(response.status)
            if (response.status === 201) {
                setDetail("Register Success");
                console.log("EHRHEJFGJ")
                navigate("/login")
            }
            else if (response.status === 400){
                const data = await response.json();
                alert(data.detail)
            }
            else {
                const data = await response.json();
                alert(data.detail[0].msg)
            }
        } catch (error) {
            console.error('An error occurred', error);
            alert("Invalid credentials ");
        }
    };
    return (
        <div>
            <NavBar/>
            <form onSubmit={handleRegister} className={"login-form"}>
                <div className="input-field">
                    <label className="input-label">Email: </label>
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required={true}
                        className="input-input"  // Added style class
                    />
                </div>

                <div className="input-field">
                    <label className="input-label">Password: </label>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required={true}
                        className="input-input"  // Added style class
                    />
                </div>

                <div className="input-field">
                    <label className="input-label">Username: </label>
                    <input
                        type="text"
                        placeholder="First name"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required={true}
                        className="input-input"  // Added style class
                    />
                </div>

                <div className="input-field">
                    <label className="input-label">First Name: </label>
                    <input
                        type="text"
                        placeholder="First name"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="input-input"  // Added style class
                    />
                </div>

                <div className="input-field">
                    <label className="input-label">Last Name: </label>
                    <input
                        type="text"
                        placeholder="Last name"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="input-input"  // Added style class
                    />
                </div>

                <button type="submit" className="input-button">Register</button>
                <h3>{detail}</h3>
            </form>

        </div>
    );
};

export default RegisterForm;