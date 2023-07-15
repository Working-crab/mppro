import axios from 'axios'
import config from '../config/'

function getHttpRequester () {
  const requester = axios.create({
    baseURL: config.baseURL,
  });
  return requester;
}

const httpRequester = getHttpRequester()

export default httpRequester
