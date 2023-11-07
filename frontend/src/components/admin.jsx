import React, {useState, useEffect} from "react";
import NavBar from "./navbar";
import {getRequestWithAuth} from "../utils/requests";


const AdminComponent = () => {
    const [isAdmin, setIsAdmin] = useState(false)
    const [detail, setDetail] = useState('')

    const checkAdminRights = async () => {
        const response = await getRequestWithAuth('/auth/admin');
        if (response.status === 403){
            setDetail('Forbidden');
            setIsAdmin(false);
        }
        if (response.status === 200){
            setIsAdmin(true);
        }
    }
    useEffect(() => {
        checkAdminRights();
    }, []);
    return (
        <div>
            <NavBar/>
            {isAdmin && (
                <div>
                    <h3>Success</h3>
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