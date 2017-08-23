var config = {//The config object provides data to read from the database that was created
    apiKey: "AIzaSyCiQxQiDulHdKwPZdj-E78SiK9rVc2HVII",
    authDomain: "prog-c99a8.firebaseapp.com",
    databaseURL: "https://prog-c99a8.firebaseio.com",
    storageBucket: "prog-c99a8.appspot.com",
    messagingSenderId: "614502053305"
};
firebase.initializeApp(config);
var data;
var hours = [];
var graphCars = [];
var position = 0;
var NumberOfCars = 0
var carsPerDay;
var carsPerDayData = [];
var context = $('#myChart');
var database = firebase.database().ref('/Pi 1/2016');//we specify the child of the data tree which we would like to read from.
database.on('value', function(snapshot){//this callback is called whenever a change is made to the databse.
    data = snapshot.val();//take a snapshot of the current data
    console.log(data);
    var currentMonth = data['October'];
    console.log(currentMonth);
    var days = [];
    numMonthCars = 0;
    for(var key in currentMonth){//For every attribute under the current month, we put that attribute in an array.
        days.push(key);
    }
    console.log(days);
    //we must sort through and extract the neccassary data retrieved from firebase.
    for(var i = 0; i < days.length; i++){
        carsPerDay = 0;
        myDay = currentMonth[days[i]];
        var keys = Object.keys(myDay);
        for(var j = 0; j < keys.length;j++){
            var hour = myDay[keys[j]];
            var minutes = Object.keys(hour);
            for(k = 0; k < minutes.length; k++){
                carsPerDay += hour[minutes[k]]['No Of Cars'];//we calculate the total number of cars for every day. 
            }
        }
        carsPerDayData[i] = carsPerDay;
    }
    console.log(carsPerDayData);
    var graphData = {//we create a graph object that would be used to create our barchart. 
        labels: days, 
        datasets: [
            {
                label: "October",
                fill: false,
                lineTension: 0.1,
                backgroundColor: "rgb(18, 4, 128)",
                borderColor: "rgba(75,192,192,1)",
                borderCapStyle: 'butt',
                borderDash: [],
                borderDashOffset: 0.0,
                borderJoinStyle: 'miter',
                pointBorderColor: "rgba(75,192,192,1)",
                pointBackgroundColor: "#fff",
                pointBorderWidth: 1, 
                pointHoverRadius: 5,
                pointHoverBackgroundColor: "rgba(75,192,192,1)",
                pointHoverBorderColor: "rgba(220,220,220,1)",
                pointHoverBorderWidth: 2,
                pointRadius: 1,
                pointHitRadius: 10,
                data: carsPerDayData,
                spanGaps: false,
            }
        ]
    };
    var myBarChart = new Chart(context, {
        type: 'bar',
        data : graphData,
        options: {
            legend: {
                text: "My Graph",
                position: "bottom",
                display: true,
                labels: {
                    fontColor: 'rgb(18, 4, 128)'
                }
            },
            title: {
                display: true,
                text: "Number of Cars per day"
            }
        }
    });
    
});
