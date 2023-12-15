import {useNavigate} from "react-router-dom";

const LogOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    const navigate = useNavigate();
    document.cookie = "email=" + "" + "; SameSite=strict" + "; max-age=" + 0;
    navigate('/login')
    return (
        <h3>Logged out</h3>
    )
}

export default LogOut;