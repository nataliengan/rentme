import React from 'react';
import ReactDOM from 'react-dom';
// import { Provider } from 'react-redux';
// import { createStore } from 'redux';
import { BrowserRouter } from 'react-router-dom'
// import reducers from './reducers';
// import '../style/style.css';
import App from './components/app';

// const Store = createStore(reducers);

ReactDOM.render(
  // <Provider store={ Store }>
  <BrowserRouter onUpdate={() => window.scrollTo(0, 0)}>
    <App />
  </BrowserRouter>
  // </Provider>
  , document.getElementById('root'));
