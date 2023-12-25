import '../styles/styles.css'
import React from 'react';


const Popup = ({content, setActive}) => {
    return (
        <div className='popup' onClick={() => setActive(false)}>
            <div className='popup_content' onClick={e => e.stopPropagation()}>
                {content}
            </div>
        </div>
    );
};

export default Popup;