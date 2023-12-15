import React, {useState, useEffect} from "react";
import NavBar from "./navbar";
import {bodyRequestWithAuth, getRequestWithAuth} from "../utils/requests";
import GamesComponent from "./games";
import '../styles/core.css';
import '../styles/pie-chart.css';
import '../styles/styles.css';
import {useNavigate} from "react-router-dom";


const AdminComponent = () => {
    const [isAdmin, setIsAdmin] = useState(false);
    const [detail, setDetail] = useState('');
    const [popularGame, setMostPopularGame] = useState([]);
    const [streamsAmount, setStreamsAmount] = useState(0);
    const [emailHostUser, setEmailHostUser] = useState('');
    const [subscriptionStreams, setSubscriptionStreams] = useState(0);
    const [notificationsAmount, setNotificationsAmount] = useState(0);
    const [dump, setDump] = useState('');
    const [restoreStatus, setRestoreStatus] = useState(false);

    const navigate = useNavigate();

    const processFileDownload = async () => {
        const response = await getRequestWithAuth('/auth/dump');
        const fileUrl = URL.createObjectURL(await response.blob());
        const link = document.createElement("a");
        link.style.display = "none";
        link.href = fileUrl;
        link.download = 'userdump.json';
        document.body.appendChild(link);
        link.click();
        URL.revokeObjectURL(link.href);
        document.body.removeChild(link);
    }
    const checkAdminRights = async () => {
        try {
            const response = await getRequestWithAuth('/auth/admin');
            if (response.status === 403) {
                setDetail('Forbidden');
                setIsAdmin(false);
            }
            if (response.status === 200) {
                setIsAdmin(true);
            }
        } catch (error) {
            if (error === 'noAuth') {
                navigate("/login");
                setIsAdmin(false);
            }
        }
    }
    const getStreamsStatistic = async () => {
        try {
            const response = await getRequestWithAuth('/twitch/reports/stream');
            if (response.status === 403) {
                setDetail('Forbidden');
                setIsAdmin(false);
            }
            const data = await response.json();

            setMostPopularGame(data.most_popular_games);
            setStreamsAmount(data.streams_amount);
        } catch (error) {

        }
    }

    const getNotificationStatistic = async () => {
        try {
            const response = await getRequestWithAuth('/twitch/reports/notification');
            if (response.status === 403) {
                setDetail('Forbidden');
                setIsAdmin(false);
            }
            const data = await response.json();
            setNotificationsAmount(data.notifications_amount);
            setEmailHostUser(data.email_host_user);
            setSubscriptionStreams(data.started_subscribed_streams);
        } catch (error) {
        }
    }

    const handleFileChange = (event) => {
        event.preventDefault();
        setDump(event.target.files[0]);
    }

    const restoreUsersFromDump = async (event) => {
        event.preventDefault();
        const formData = new FormData();
        if (dump) {
            formData.append('file', dump, 'dump.json');
            console.log(formData);
            try {
                const response = await bodyRequestWithAuth('/auth/dump', formData, "POST", true, true);
                if (response.status === 200) {
                    setRestoreStatus(true);
                }
                else {
                    alert("bad data")
                }
            }
            catch (error){
                alert("bad data");
            }
        }
    }
    useEffect(() => {
        checkAdminRights();
        getStreamsStatistic();
        getNotificationStatistic();
    }, []);
    return (
        <div>
            <NavBar/>
            {isAdmin && (
                <div>
                    <h3>Success</h3>
                    <div className='container'>
                        <h4 style={{textAlign: "center"}}>Today's most popular game</h4>
                        <GamesComponent games={popularGame}/>
                    </div>
                    <div className='center-border'>
                        <h4>Today's streams amount <span
                            className="badge bg-primary rounded-pill">{streamsAmount}</span></h4>
                        <h4>Messages were sent from <span
                            className="badge bg-primary rounded-pill">{emailHostUser}</span></h4>
                        <h4>Today's subscribed streams amount <span
                            className="badge bg-primary rounded-pill">{subscriptionStreams}</span></h4>
                        <h4>Today's notifications amount <span
                            className="badge bg-primary rounded-pill">{notificationsAmount}</span></h4>
                        <div className='center'>
                            <button onClick={processFileDownload} className="badge bg-primary rounded-pill">Download
                                User Dump
                            </button>
                        </div>
                        <div className='center'>
                            <form method='POST' onSubmit={restoreUsersFromDump}>
                                <div>
                                    <label>Restore users from file:</label>
                                    <input onChange={handleFileChange} type="file"/>
                                    <button type={"submit"}>Save</button>
                                </div>
                            </form>
                            {restoreStatus && (
                                <div>
                                    <h6>Restored users from your file</h6>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
            {!isAdmin && (
                <div>
                    <h3>{detail}</h3>
                </div>
            )}
        </div>
    )
}

export default AdminComponent