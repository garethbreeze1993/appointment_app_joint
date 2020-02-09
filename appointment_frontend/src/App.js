import React, { Component } from 'react';
import PropTypes from 'prop-types';
import logo from './logo.svg';
import './App.css';

class App extends Component {
    state = {
		Appointments_List: [
			
    {
        "id": 1,
        "times": {
            "id": 1,
            "time_start": "09:00:00",
            "time_end": "2020-02-09T09:30:00Z",
            "date_start": "2020-02-09"
        },
        "filled": true,
        "client": "aladdin"
    }

		]
	}
    render(){
        return(
        <h1>Hello {this.state.Appointments_List[0].client}</h1>
        )
    }
}

export default App;
