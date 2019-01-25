
let rooms_list = [];
for (let n of _.range(101, 105)) {
    rooms_list.push(n)// { id: n.toString(), floor: "100", title: n });
}
for (let etage of _.range(2, 6)) {
    for (let n of _.range(1, 9)) {
        let room = etage * 100 + n
        rooms_list.push(room)// { id: room.toString(), floor: (etage*100).toString(), title: room });
    }
}



let app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        message: 'Hello',
        date_start: moment().subtract(10, 'days'),
        date_end: moment().add(20, 'days'),
        rooms_list: rooms_list,
        room_type_list: ["Single Eco", "Single Balcony", "Double Eco", "Double Balcony", "Triple Eco", "Triple Balcony"],
        booking_data: [],
        display: "booking" // "booking", "price"
    },
    mounted: function() {
        this.$nextTick(function() {
            $.get("/api/stay/" + this.date_start.format("YYYY-MM-DD") + "/" + this.date_end.format("YYYY-MM-DD"),
            function(data) {
                app.booking_data = data;
            })
        })
    },
    computed: {
        period_range: function() {
            res = []
            for (let i of _.range( moment.duration(this.date_end - this.date_start).asDays() )) {
                res.push(moment(this.date_start + moment.duration(i, 'days')));
            }
            return res;
        }
    },
    methods: {
        booking: function(room, date) {
            let booking_data_in_room = this.booking_data.filter(data => data.room === room)
                                                        .filter(data => moment(data.start) <= date && moment(data.end) > date)
            if (booking_data_in_room.length > 0) {
                return {title: booking_data_in_room[0].title}
            }
            return {title: ""}
        },
        price: function(room, date) {
            return Math.floor((Math.random() * 40) + 44);;
        },
        switchTo: function(display){
            this.display = display;
        }
    },
});

// updateDateCalendar: function() {
//     $('#calendar').fullCalendar({
//         header: {
//             center: 'calendarBooking' // buttons for switching between views
//         },
//         aspectRatio: 3,
//         now: this.date_start.date,
//         editable: true,
//         defaultView: 'calendarBooking',
//         views: {
//             calendarBooking: {
//                 type: 'timeline',
//                 duration: { days: 30 },
//                 buttonText: 'normal'
//             }
//         },
//         resourceGroupField: 'floor',
//         resources: list_rooms,
//         events: {
//             url: "/api/stay/" + this.date_start.date.format("YYYY-MM-DD") + "/" + this.date_end.format("YYYY-MM-DD"),
//             error: function() {
//                 $('#script-warning').show();
//             }
//         }
//     });
//     return this.date_start.date;
// }