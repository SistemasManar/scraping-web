const puppeteer = require('puppeteer');
const request = require('request-promise-native');
const poll = require('promise-poller').default;

const siteDetails = {
  sitekey: '6LeJaRUUAAAAAA2iQkfdLPkK-vJ2mBqs8j_XA2-t',
  pageurl: 'https://www.movistar.com.pe/movil/conoce-tus-numeros-moviles'
}

const chromeOptions = {
  executablePath:'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless:false,
  slowMo:10,
  defaultViewport: null
};

/*puppeteer.launch({ headless: true }).then(async browser => {
  const page = await browser.newPage();
  console.log(`Navigating to ${siteDetails.pageurl}`);
  await page.goto('https://www.google.com/recaptcha/api2/demo');
  const requestId = await initiateCaptchaRequest('8776bc8c354936010b98c85324142eb4');

  await page.type('#input1', 'Jose');
  await page.type('#input2', 'Miralles');
  await page.type('#input3', 'dawdadw@gmail.com');

  const response = await pollForRequestResults('8776bc8c354936010b98c85324142eb4', requestId);
  console.log(`Entering recaptcha response ${response}`);
  await page.evaluate(`document.getElementById("g-recaptcha-response").innerHTML="${response}";`);
  console.log(`Submiting...`);
  await page.click('#recaptcha-demo-submit');
  await browser.close()
})*/

(async function main() {
  const browser = await puppeteer.launch(chromeOptions);
  const page = await browser.newPage();
  console.log(`Navigating to ${siteDetails.pageurl}`);
  await page.goto('https://www.movistar.com.pe/movil/conoce-tus-numeros-moviles');
  const requestId = await initiateCaptchaRequest('8776bc8c354936010b98c85324142eb4');
  console.log(`requestID: ${requestId}`);

  await page.select('#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentType', 'RUC');
  await page.type('#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentNumber', '20492608069');
  await page.select('#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentTypeRpstative', 'DNI');
  await page.type('#_consultmobilenumbers_WAR_consultmobilenumbersportlet_documentNumberRpstative', '07820479');

  const response = await pollForRequestResults('8776bc8c354936010b98c85324142eb4', requestId);
  console.log(`Entering recaptcha response ${response}`);
  await page.evaluate(`document.getElementById("g-recaptcha-response").innerHTML="${response}";`);
  console.log(`Submiting...`);
  await page.click('#_consultmobilenumbers_WAR_consultmobilenumbersportlet_btnSubmit');
})()

async function initiateCaptchaRequest(apiKey) {
  const formData = {
    method: 'userrecaptcha',
    googlekey: siteDetails.sitekey,
    key: apiKey,
    pageurl: siteDetails.pageurl,
    json: 1
  };
  console.log(`Submiting solution request to 2captcha for ${siteDetails.pageurl}`);
  const response = await request.post('http://2captcha.com/in.php', {form: formData});
  return JSON.parse(response).request;
}

async function pollForRequestResults(key, id, retries = 30, interval = 1500, delay = 2000) {
  console.log(`Waiting for ${delay} miliseconds...`);
  await timeout(delay);
  return poll({
    taskFn: requestCaptchaResults(key, id),
    interval,
    retries
  });
}

function requestCaptchaResults(apiKey, requestId) {
  const url = `http://2captcha.com/res.php?key=${apiKey}&action=get&id=${requestId}&json=1`;
  return async function() {
    return new Promise(async function(resolve, reject){
      console.log(`Polling for response..`);
      const rawResponse = await request.get(url);
      const resp = JSON.parse(rawResponse);
      console.log(resp);
      if (resp.status === 0) return reject(resp.request);
      console.log(`Response received`)
      resolve(resp.request);
    });
  }
}

const timeout = millis => new Promise(resolve => setTimeout(resolve, millis))
