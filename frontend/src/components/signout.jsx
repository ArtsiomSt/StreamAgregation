import {useNavigate} from "react-router-dom";
import React from "react";
import "../styles/login.css"

const LogOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    const navigate = useNavigate();
    document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
    const handleRegisterRedirect = async () => {
        navigate('/login')
    }
    return (
        <h3>Logged out, to login use <button onClick={handleRegisterRedirect} className={"input-button"}>Login</button></h3>
    )
}

export default LogOut;