import {bodyRequestWithAuth, getRequestWithAuth, getRequest} from "../utils/requests";
import {useNavigate} from "react-router-dom";
import React, {useState, useEffect} from "react";
import NavBar from "./navbar"
import {getCookie} from "../utils/utils";
import '../styles/core.css'


const ProfileComponent = () => {
    const [id, setId] = useState(0);
    const [email, setEmail] = useState('');
    const [firstName, setFirstName] = useState('');
    const [username, setUsername] = useState('')
    const [lastName, setLastName] = useState('');
    const [isEmailVerified, setEmailVerified] = useState(false);
    const [newEmail, setNewEmail] = useState('');
    const [detail, setDetail] = useState('');
    const [verificationDetail, setVerificationDetail] = useState('');
    const [newFirstName, setNewFirstName] = useState('');
    const [newUsername, setNewUsername] = useState('')
    const [newLastName, setNewLastName] = useState('');
    const navigate = useNavigate();

    const getProfile = async () => {
        try {
            const response = await getRequestWithAuth('/auth/me');
            const data = await response.json();
            document.cookie = "email=" + data.email + "; SameSite=strict" + "; max-age=" + 24 * 3600
            setId(data.id)
            setEmail(data.email);
            setUsername(data.username);
            setFirstName(data.first_name);
            setLastName(data.last_name);
            setEmailVerified(data.is_email_verified)
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    const handleChangeProfileInfo = async (e) => {
        e.preventDefault();
        try {
            const body = {
                "email": email,
                "first_name": newFirstName,
                "last_name": newLastName,
                "username": newUsername
            };
            if (newUsername === username && newLastName === lastName && firstName === firstName) {
                setDetail("You have to change something in your profile")
            } else {
                const response = await bodyRequestWithAuth('/auth/me', body, 'PATCH');
                await getProfile();
                setNewLastName('');
                setNewFirstName('');
                setNewUsername('');
            }
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    const handleEmailVerify = async () => {
        try {
            const cooldown = getCookie('cooldown')
            if (cooldown === undefined) {
                document.cookie = "cooldown=" + 1 + "; SameSite=strict" + "; max-age=" + 60;
                const response = await getRequestWithAuth('/auth/email/send-verify-email');
                setVerificationDetail("");
            } else {
                setVerificationDetail("You have to wait 1 minute till next verify request");
            }
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    useEffect(() => {
        getProfile();
    }, []);
    return (
        <div>
            <NavBar/>
            <div className="container">
                <div>
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
                <div className='center-border'>
                    <form onSubmit={handleChangeProfileInfo}>
                        <div>
                            <label>Username: </label>
                            <input
                                type="text"
                                placeholder="new username"
                                value={newUsername}
                                onChange={(e) => setNewUsername(e.target.value)}
                                required={true}
                            />
                        </div>
                        <div>
                            <label>First Name: </label>
                            <input
                                type="text"
                                placeholder="new first name"
                                value={newFirstName}
                                onChange={(e) => setNewFirstName(e.target.value)}
                            />
                        </div>
                        <div>
                            <label>Last Name: </label>
                            <input
                                type="text"
                                placeholder="new last name"
                                value={newLastName}
                                onChange={(e) => setNewLastName(e.target.value)}
                            />
                        </div>
                        <button type="submit">Submit</button>
                        <h3>{detail}</h3>
                    </form>
                    {isEmailVerified === false && (
                        <div className='center'>
                            <h6>Your email is not verified &nbsp;
                                <button onClick={handleEmailVerify}>Verify</button>
                            </h6>
                            <h6>{verificationDetail}</h6>
                        </div>
                    )}
                    {isEmailVerified === true && (
                        <div className='center'>
                            <h6>Your email is verified
                            </h6>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ProfileComponent;