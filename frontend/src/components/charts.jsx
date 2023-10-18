import {useState, useEffect} from "react";
import NavBar from "./navbar";
import {deleteRequestWithAuth, getRequestWithAuth} from "../utils/requests";
import {useNavigate} from "react-router-dom";


const ChartsComponent = () => {
    const [recommendations, setRecommendations] = useState([]);
    const navigate = useNavigate();

    const getRecommendations = async () => {
        try {
            const response = await getRequestWithAuth("/twitch/user/recommendations");
            const data = await response.json();
            data.forEach(streamer => {
                streamer.action = "subscribe";
            })
            setRecommendations(data);
        } catch (error) {
            if (error === "noAuth") {
            }
        }
    }
    const handleSubscription = async (streamer_id, action) => {
        try {
            if (action === "subscribe") {
                const response = await getRequestWithAuth('twitch/users/subscribe/' + streamer_id);
                recommendations.forEach(streamer => {
                    if (streamer.twitch_user_id === streamer_id) {
                        streamer.action = "Already in subscriptions";
                    }
                })
                recommendations.forEach(streamer => {
                    console.log(streamer.action);
                })
                let new_recommendations = []
                console.log(recommendations.length)
                for (let i = 0; i < recommendations.length; i++) {
                    if (recommendations[i].twitch_user_id !== streamer_id) {
                        new_recommendations.push(recommendations[i])
                    }
                }
                console.log(new_recommendations.length)
                setRecommendations(new_recommendations)
            }
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }
    useEffect(() => {
        getRecommendations();
    }, []);
    return (
        <div>
            <NavBar/>
            <h3>Works</h3>
            <ol className="list-group list-group-numbered">
                {recommendations.map((item) => (
                    <li className="list-group-item d-flex justify-content-between align-items-start">
                        <div className="ms-2 me-auto">
                            <div className="fw-bold">{item.display_name}</div>
                            login - {item.login}
                        </div>
                        <a href="#" onClick={() => handleSubscription(item.twitch_user_id, 'subscribe')}><span className="badge bg-primary rounded-pill">{item.action}</span></a>
                    </li>
                ))}
            </ol>
        </div>
    )
}

export default ChartsComponent;