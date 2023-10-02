import {getRequestWithAuth} from "../utils/requests";
import {useNavigate} from "react-router-dom";
import {useState, useEffect} from "react";


const ProfileComponent = () => {
    const [id, setId] = useState(0);
    const [email, setEmail] = useState('');
    const [firstName, setFirstName] = useState('');
    const [username, setUsername] = useState('')
    const [lastName, setLastName] = useState('');

    const navigate = useNavigate();
    const getProfile = async () => {
        try {
            const response = await getRequestWithAuth('/auth/me');
            const data = await response.json();
            setId(data.id)
            setEmail(data.email);
            setUsername(data.username);
            setFirstName(data.first_name);
            setLastName(data.last_name);
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }
    useEffect(() => {
        getProfile()
    }, []);
    return (
        <div className="container">
            <h1>Your profile info</h1>
            <table className="table">
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <td>{id}</td>
                    <td>{username}</td>
                    <td>{email}</td>
                    <td>{firstName}</td>
                    <td>{lastName}</td>
                </tr>
                </tbody>
            </table>
        </div>
    )
}

export default ProfileComponent;