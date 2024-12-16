import NavBar from "./navbar";
import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom";
import {bodyRequestWithAuth, deleteRequestWithAuth} from "../utils/requests";
import "../styles/search.css";


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
                        <button type="submit" className={"search-button"}>Search</button>
                    </div>
                </form>
            </div>
            <br/>
            <h4>Streamers</h4>
            <hr/>
            <div className='table-container'>
                <table>
                    <tr>
                        <th>id</th>
                        <th>Login</th>
                        <th>Display Name</th>
                        <th>Description</th>
                        <th>Subscribe</th>
                    </tr>
                    {subscriptions.map((item) => (
                        <tr>
                            <td>{item.id}</td>
                            <td>{item.login}</td>
                            <td>{item.display_name}</td>
                            <td>{item.description}</td>
                            <td><a onClick={() => handleSubscription(item.twitch_user_id)}
                                   href="#"><span
                                className="badge bg-primary rounded-pill">unsubscribe</span></a></td>
                        </tr>
                    ))}
                </table>
            </div>
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