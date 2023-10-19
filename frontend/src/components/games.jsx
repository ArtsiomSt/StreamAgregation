import React, {useEffect, useState} from "react";


const GamesComponent = ({games}) => {
    return (
        <div>
            {games.map((game) =>(
                <ul className="list-group">
                    <li className="list-group-item active" aria-current="true">{game.game_name}</li>
                </ul>))}
        </div>)
}

export default GamesComponent;