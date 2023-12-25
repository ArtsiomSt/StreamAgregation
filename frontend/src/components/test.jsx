import React, { useState } from 'react';
import {Navigate, useNavigate} from "react-router-dom";
import { getRequestWithAuth, bodyRequestWithAuth } from "../utils/requests.jsx";

const TestForm = () => {
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
            try {
                const response = await getRequestWithAuth("/auth/test")
                const data = await response.json()
                setDetail(data.detail)
            }
            catch (error){
                if (error === "noAuth"){
                    navigate('/login')
                }
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
                    type="text"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required={true}
                />
            </div>
      <button type="submit">Register</button>
      <h3>{detail}</h3>
    </form>
  );
};

export default TestForm;