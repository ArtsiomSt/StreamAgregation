import {useNavigate} from "react-router-dom";
import React, {useEffect, useState} from "react";
import {bodyRequestWithAuth, bodyRequest, deleteRequestWithAuth, getRequestWithAuth} from "../utils/requests";
import GamesComponent from "./games";
import Popup from "../utils/popup";
import NavBar from "./navbar";
import '../styles/table.css';
import '../styles/search.css'


const StreamersComponent = () => {
    const [currentPage, setCurrentPage] = useState(1);
    const [data, setData] = useState([]);
    const [subscriptions, setSubscriptions] = useState([]);
    const [search, setSearch] = useState('');
    const [showPopup, setShowPopup] = useState(false);
    const [popupContent, setPopupContent] = useState("");
    const [searchGame, setSearchGame] = useState("");
    const [games, setGames] = useState([]);

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
            if (searchByGame) {
                body['search_value'] = searchByGame;
                url = '/twitch/games/streamers';
            }
            const response = await bodyRequest(url, body);
            if (searchByGame){
                url = '/twitch/games/query';
                const gamesResponse = await bodyRequest(url, body);
                const gamesData = await gamesResponse.json();
                setGames(gamesData);
            }
            else {
                setGames([])
            }
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
                <form onSubmit={handleSearch} className="search-form">
                    <div className="inputs-row">
                        <div className="search-field">
                            <label className="search-label">Streamer: </label>
                            <input
                                type="search"
                                placeholder="Enter streamer name"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="search-input"
                                required={false}
                            />
                        </div>

                        <div className="search-field">
                            <label className="search-label">Game: </label>
                            <input
                                type="search"
                                placeholder="Enter game title"
                                value={searchGame}
                                onChange={(e) => setSearchGame(e.target.value)}
                                className="search-input"
                                required={false}
                            />
                        </div>

                        <button type="submit" className="search-button">Search</button>
                    </div>
                </form>
            </div>
            <br/>
            {games.length !== 0 && (
                <div>
                    <h3>Games matching your request</h3>
                    <GamesComponent games={games}/>
                </div>
            )}
            <h3>Streamers</h3>
            {showPopup && (
                <div>
                    <Popup content={popupContent} setActive={setShowPopup}/>
                </div>
            )}
            <div className='table-container'>
                <table>
                    <tr>
                        <th>id</th>
                        <th>Login</th>
                        <th>Display Name</th>
                        <th>Description</th>
                        <th>Subscribe</th>
                    </tr>
                    {data.map((item) => (
                        <tr>
                            <td>{item.id}</td>
                            <td>{item.login}</td>
                            <td>{item.display_name}</td>
                            <td>{item.description}</td>
                            <td><a onClick={() => handleSubscription(item.twitch_user_id, item.action)} href="#"><span
                                className="badge bg-primary rounded-pill">{item.action}</span></a></td>
                        </tr>
                    ))}
                </table>
            </div>
            <div>
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
        </div>
    );
}

export default StreamersComponent;