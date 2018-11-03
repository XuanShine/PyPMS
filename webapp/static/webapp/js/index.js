// $('#calendar').fullCalendar({
//     defaultView: 'timelineMonth'
// });

let list_rooms = [];
for (let n in _.range(4)) {
    let room = 101 + Number(n);
    list_rooms.push({ id: room.toString(), floor: "100", title: room });
}
for (let etage in _.range(4)) {
    for (let n in _.range(8)) {
        let room = (Number(etage) + 2) * 100 + Number(n) + 1
        list_rooms.push({ id: room.toString(), floor: ((Number(etage) + 2) * 100).toString(), title: room });
    }
}

// let stays = [{"check_in": "2018-11-01", "check_out": "2018-11-02", "name": "Dupont", "room": 101, "status": 1}, {"check_in": "2018-11-03", "check_out": "2018-11-05", "name": "Tartagnan", "room": 103, "status": 1}, {"check_in": "2018-10-31", "check_out": "2018-11-04", "name": "Emmanuel", "room": 101, "status": 1}];
// let stays_events = []
// for (const [n, stay] of stays.entries()) {
//     stays_events.push(
//         { id: n.toString(), resourceId: stay.room.toString(), start: stay.check_in.toString(), end: stay.check_out.toString(), title: stay.name }
//     )
// }

$('#calendar').fullCalendar({
    header: {
        center: 'calendarBooking' // buttons for switching between views
    },
    aspectRatio: 3,
    now: '2018-10-20',
    editable: true,
    defaultView: 'calendarBooking',
    views: {
        calendarBooking: {
            type: 'timeline',
            duration: { days: 30 },
            buttonText: 'normal'
        }
    },
    resourceGroupField: 'floor',
    resources: list_rooms,
    events: {
        url: "/api/stay/2018-10-29/2018-11-10",
        error: function() {
            $('#script-warning').show();
        }
    }
});