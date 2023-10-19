import {useState, useEffect} from "react";
import NavBar from "./navbar";
import {getRequestWithAuth, bodyRequestWithAuth} from "../utils/requests";
import {useNavigate} from "react-router-dom";
import GamesComponent from "./games";


const ChartsComponent = () => {
    const [recommendations, setRecommendations] = useState([]);
    const [games, setGames] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    const navigate = useNavigate();

    const updateExistingRecommendations = (recommendations, subscriptions) => {
        let updated_recommendations = [];
        for (let i = 0; i < recommendations.length; i++) {
            let notFound = true;
            for (let j = 0; j < subscriptions.length; j++) {
                if (recommendations[i].twitch_user_id === subscriptions[j].twitch_user_id) {
                    notFound = false;
                    break;
                }
            }
            if (notFound) {
                updated_recommendations.push(recommendations[i]);
            }
        }
        setRecommendations(updated_recommendations);
    }

    const getSubscriptions = async () => {
        try {
            const response = await bodyRequestWithAuth(
                '/twitch/user/subscriptions', {"paginate_by": 100, "page_num": 0}, "POST"
            );
            const data = await response.json();
            setSubscriptions(data);
            return data;
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    const getRecommendations = async () => {
        try {
            const response = await getRequestWithAuth("/twitch/user/recommendations");
            const usersGamesResponse = await getRequestWithAuth('/twitch/user/games');
            const gamesData = await usersGamesResponse.json();
            const data = await response.json();
            setGames(gamesData);
            data.forEach(streamer => {
                streamer.action = "subscribe";
            })
            const subs = await getSubscriptions();
            setRecommendations(data);
            updateExistingRecommendations(data, subs);
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
                let new_recommendations = []
                for (let i = 0; i < recommendations.length; i++) {
                    if (recommendations[i].twitch_user_id !== streamer_id) {
                        new_recommendations.push(recommendations[i])
                    }
                }
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
            <div>
                <h3>Your top games</h3>
                <GamesComponent games={games}/>
            </div>
            <h3>Your recommendations</h3>
            {recommendations.length === 0 && (
                <h2><p>It seems like you don't have new recommendations</p><p>Wait for next partition</p></h2>)}
            {recommendations.length !== 0 && (<ol className="list-group list-group-numbered">
                {recommendations.map((item) => (
                    <li className="list-group-item d-flex justify-content-between align-items-start">
                        <div className="ms-2 me-auto">
                            <div className="fw-bold">{item.display_name}</div>
                            login - {item.login}
                        </div>
                        <a href="#" onClick={() => handleSubscription(item.twitch_user_id, 'subscribe')}><span
                            className="badge bg-primary rounded-pill">{item.action}</span></a>
                    </li>
                ))}
            </ol>)}
        </div>
    )
}

export default ChartsComponent;