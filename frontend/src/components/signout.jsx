import {useNavigate} from "react-router-dom";

const LogOut = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    const navigate = useNavigate();
    navigate('/login')
    return (
        <h3>Logged out</h3>
    )
}

export default LogOut;