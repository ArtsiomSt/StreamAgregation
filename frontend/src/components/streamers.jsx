import {useNavigate} from "react-router-dom";
import React, {useEffect, useState} from "react";
import {bodyRequestWithAuth, bodyRequest, deleteRequestWithAuth, getRequestWithAuth} from "../utils/requests";
import Popup from "../utils/popup";
import NavBar from "./navbar"


const StreamersComponent = () => {
    const [currentPage, setCurrentPage] = useState(1);
    const [data, setData] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    const [search, setSearch] = useState('');
    const [showPopup, setShowPopup] = useState(false);
    const [popupContent, setPopupContent] = useState("");
    const [searchGame, setSearchGame] = useState("");

    const navigate = useNavigate();

    const handleClick = () => {
        setShowPopup(true);
    };

    const handleClose = () => {
        setShowPopup(false);
    };

    const getStreamers = async (pageNumber, search = '', searchByGame = '') => {
        try {
            const body = {"paginate_by": 20, "page_num": pageNumber - 1};
            if (search) {
                body['search_streamer'] = search;
            }
            let url = '/twitch/streamers'
            if (searchByGame){
                body['search_value'] = searchByGame;
                url = '/twitch/games/streamers';
            }
            const response = await bodyRequest(url, body);
            setData(await response.json());
        } catch (error) {
            console.log(error);
        }
    }

    const handleSearch = async (e) => {
        e.preventDefault();
        setCurrentPage(1);
        await getStreamers(1, search, searchGame);
    }
    const handlePageClick = async (pageNumber) => {
        setCurrentPage(pageNumber);
        await getStreamers(pageNumber, search, searchGame);
    };

    const getSubscriptions = async () => {
        try {
            const response = await bodyRequestWithAuth(
                '/twitch/user/subscriptions', {"paginate_by": 100, "page_num": 0}, "POST"
            );
            setSubscriptions(await response.json());
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    const handleSearchGame = async (e) => {
        e.preventDefault();

    }

    const handleSubscription = async (streamer_id, method) => {
        try {
            if (method === 'subscribe') {
                const response = await getRequestWithAuth('twitch/users/subscribe/' + streamer_id);
                if (response.status === 403) {
                    const data = await response.json()
                    setPopupContent(data.detail)
                    setShowPopup(true)
                    return
                }
            }
            if (method === 'unsubscribe') {
                const response = await deleteRequestWithAuth('twitch/users/subscribe/' + streamer_id);
            }
            const actions = {'subscribe': 'unsubscribe', 'unsubscribe': 'subscribe'};
            data.forEach(streamer => {
                if (streamer.twitch_user_id === streamer_id) {
                    streamer.action = actions[streamer.action];
                }
            })
            await getSubscriptions();
            updateAction();
        } catch (error) {
            if (error === 'noAuth') {
                navigate('/login')
            }
        }
    }

    useEffect(() => {
        getStreamers(currentPage);
        getSubscriptions();
    }, []);
    const updateAction = () => {
        data.forEach(streamer => {
            streamer['action'] = 'subscribe';
            subscriptions.forEach(subscription => {
                if (subscription.twitch_user_id === streamer.twitch_user_id) {
                    streamer['action'] = 'unsubscribe';
                }
            })
        })
    }
    updateAction()
    return (
        <div>
            <NavBar/>
            <div>
                <form onSubmit={handleSearch}>
                    <div>
                        <label>Streamer: </label>
                        <input
                            type="search"
                            placeholder="streamer"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            required={false}
                        />
                    </div>
                    <div>
                        <label>Game: </label>
                        <input
                            type="search"
                            placeholder="game"
                            value={searchGame}
                            onChange={(e) => setSearchGame(e.target.value)}
                            required={false}
                        />
                    </div>
                    <button type="submit">Search</button>
                </form>
            </div>
            <br/>
            <h4>Streamers</h4>
            <hr/>
            {showPopup && (
                <div>
                    <Popup content={popupContent} setActive={setShowPopup}/>
                </div>
            )}
            {data.map((item) => (
                <div>
                    <ol className="list-group list-groupd">
                        <li className="d-flex justify-content-between align-items-start">
                            <div className="ms-2 me-auto">
                                <div className="fw-bold">{item.id}</div>
                                <div className="fw-bold">Display name: {item.display_name}, login : {item.login}</div>
                                {item.description}
                                <hr/>
                            </div>
                            <a onClick={() => handleSubscription(item.twitch_user_id, item.action)} href="#"><span
                                className="badge bg-primary rounded-pill">{item.action}</span></a>
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
                    {data.length === 20 && (
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

export default StreamersComponent;