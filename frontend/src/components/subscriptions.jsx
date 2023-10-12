import NavBar from "./navbar";
import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import {bodyRequestWithAuth, deleteRequestWithAuth} from "../utils/requests";
import {get} from "axios";


const SubscriptionsComponent = () => {
    const navigate = useNavigate();
    const [subscriptions, setSubscriptions] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [search, setSearch] = useState('');

    const getSubscriptions = async (pageNumber, search = '') => {
        try {
            const body = {"paginate_by": 20, "page_num": pageNumber - 1}
            if (search){
                body['search_streamer'] = search
            }
            const response = await bodyRequestWithAuth(
                '/twitch/user/subscriptions', body, "POST"
            );
            setSubscriptions(await response.json());
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    const handleSearch = async (e) => {
        e.preventDefault();
        setCurrentPage(1);
        await getSubscriptions(1, search);
    }

    const handlePageClick = async (pageNumber) => {
        setCurrentPage(pageNumber);
        await getSubscriptions(pageNumber, search);
    };

    const handleSubscription = async (streamer_id) => {
        try {
            const response = await deleteRequestWithAuth('twitch/users/subscribe/' + streamer_id);
            await getSubscriptions(currentPage);
            // for (let i = 0; i<subscriptions.length; i++){
            //     if (subscriptions[i].twitch_user_id === streamer_id){
            //         subscriptions.splice(i, 1);
            //         break;
            //     }
            // }
            // setSubscriptions(subscriptions)
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }

    }
    useEffect(() => {
        getSubscriptions(currentPage);
    }, [])
    return (
        <div>
            <NavBar/>
            <div>
                <form onSubmit={handleSearch}>
                    <div>
                        <label>Search: </label>
                        <input
                            type="search"
                            placeholder="streamer"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            required={false}
                        />
                    </div>
                    <button type="submit">Search</button>
                </form>
            </div>
            <br/>
            <h4>Streamers</h4>
            <hr/>
            {subscriptions.map((item) => (
                <div>
                    <ol className="list-group list-groupd">
                        <li className="d-flex justify-content-between align-items-start">
                            <div className="ms-2 me-auto">
                                <div className="fw-bold">{item.id}</div>
                                <div className="fw-bold">Display name: {item.display_name}, login : {item.login}</div>
                                {item.description}
                                <hr/>
                            </div>
                            <a onClick={() => handleSubscription(item.twitch_user_id)} href="#"><span
                                className="badge bg-primary rounded-pill">Unsubscribe</span></a>
                        </li>
                    </ol>
                </div>
            ))}
            <nav aria-label="Page navigation example">
                <ul className="pagination">
                    {currentPage > 1 && (
                        <li className="page-item">
                            <a onClick={() => handlePageClick(currentPage - 1)} className="page-link"
                               href="#">Previous</a>
                        </li>
                    )}
                    <li className="page-item active" aria-current="page"><a className="page-link"
                                                                            href="#">{currentPage}</a></li>
                    {subscriptions.length === 20 && (
                        <li className="page-item">
                            <a onClick={() => handlePageClick(currentPage + 1)} className="page-link"
                               href="#">Next</a>
                        </li>
                    )}
                </ul>
            </nav>
        </div>
    );
}

export default SubscriptionsComponent;