import React, {useEffect, useState} from "react";


const GamesComponent = ({games}) => {
    return (
        <div className='center-border'>
            <ul style={{listStyleType: 'none', padding: '5px'}}>
                {games.map((game) => (
                    <li style={{textAlign: 'center', padding: '5px', border: '2px solid', marginBottom: '10px', borderRadius: '10px', backgroundColor: 'lightblue'}}>{game.game_name}</li>
                ))}
            </ul>
        </div>)
}

export default GamesComponent;