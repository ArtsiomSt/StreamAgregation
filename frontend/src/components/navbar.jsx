import React from "react";
import {useState, useEffect} from "react";
import {getCookie} from "../utils/utils";

const NavBar = (props) => {
    const [email, setEmail] = useState();
    const emailCookie = getCookie('email');

    return (
        <nav className="navbar navbar-expand-lg bg-light">
            <div className="container-fluid">
                <a className="navbar-brand" href="#">StreamAggregationPlatform</a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <a className="nav-link active" aria-current="page" href="/charts">Charts</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link active" aria-current="page" href="/subscriptions">My Subscriptions</a>
                        </li>
                        <li className="nav-item">
                            <a className="nav-link active" aria-current="page" href="/streamers">Streamers</a>
                        </li>
                        {emailCookie !== undefined && (
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="" href="/profile">{emailCookie}</a>
                            </li>
                        )}
                        {emailCookie === undefined && (
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="" href="/profile">Profile</a>
                            </li>
                        )}
                        {emailCookie === undefined && (
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="page" href="/login">Login</a>
                            </li>
                        )}
                        <li className="nav-item">
                            <a className="nav-link active" aria-current="page">|</a>
                        </li>
                        {emailCookie !== undefined && (
                            <li className="nav-item">
                                <a className="nav-link active" aria-current="page" href="/logout">Sign Out</a>
                            </li>
                        )}
                    </ul>
                </div>
            </div>
        </nav>
    );
}

export default NavBar;