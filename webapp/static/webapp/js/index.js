
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
        display: "booking", // "booking", "price"
        date_choosen: "",
        current_res_choosen: {},
        list_stays: [],
        current_stay_id: 0
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
                return {title: booking_data_in_room[0].title, id: booking_data_in_room[0].id}
            }
            return {title: ""}
        },
        price: function(room, date) {
            return Math.floor((Math.random() * 40) + 44);;
        },
        switchTo: function(display){
            this.display = display;
        },
        changeDate: function() {
            this.date_choosen = $("#datepicker").val();
            let day = moment(this.date_choosen);
            this.date_start = moment(day).subtract(10, 'days');
            this.date_end = moment(day).add(20, 'days');
            this.updateDateDisplay();
        },
        updateDateDisplay: function() {
            $.get("/api/stay/" + this.date_start.format("YYYY-MM-DD") + "/" + this.date_end.format("YYYY-MM-DD"),
            function(data) {
                app.booking_data = data;
            })
        },
        showReservation: function(id) {
            app.current_stay_id = id
            $.get("/api/reservation/stay/" + id,
                function(data) {
                    reservationQuery = data[0]
                    staysQuery = data[1]
                    app.current_res_choosen = reservationQuery[0]['fields']
                    app.list_stays = 0
            })
        }
    },
});

