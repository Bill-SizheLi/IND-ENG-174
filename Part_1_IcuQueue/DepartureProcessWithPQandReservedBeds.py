import heapq
from Part_1_IcuQueue.ArrivalProcess import simulate_arrival_process, generate_length_of_stays,rate_distribution_pdf

capacity = 100  # Maximum ICU capacity
reserved_capacity = 30
average_length_of_stays = [3, 7, 15]
def simulate_departure_process_priority_with_reserved(arrival_times, severity_level_list, length_of_stays, capacity=capacity, reserved_capacity=reserved_capacity):
    regular_capacity = capacity - reserved_capacity  # Regular beds
    current_regular_ICU_departures = []  # Priority queue for regular bed departures
    current_reserved_ICU_departures = []  # Priority queue for reserved bed departures
    
    departure_times = [None] * len(arrival_times)
    start_times = [None] * len(arrival_times)
    waiting_queue = []  # Priority queue for waiting patients
    
    for i in range(len(arrival_times)):
        temporary_regular_departure_time_list = []
        temporary_reserved_departure_time_list = []
        arrival_time = arrival_times[i]
        severity = severity_level_list[i]
        length_of_stay = length_of_stays[i] * 24  # Convert days to hours
        
        while current_regular_ICU_departures and current_regular_ICU_departures[0][0] <= arrival_time:
            previous_departure_time, departure_index = heapq.heappop(current_regular_ICU_departures)
            departure_times[departure_index] = previous_departure_time
            temporary_regular_departure_time_list.append(previous_departure_time)


            if waiting_queue:
                _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)
                start_time = temporary_regular_departure_time_list.pop(0)
                start_times[waiting_index] = start_time

                # Calculate departure time and add to ICU
                departure_time = start_time + length_of_stays[waiting_index] * 24
                departure_times[waiting_index] = departure_time
                heapq.heappush(current_regular_ICU_departures, (departure_time, waiting_index))


        while current_reserved_ICU_departures and current_reserved_ICU_departures[0][0] <= arrival_time:
            previous_departure_time, departure_index = heapq.heappop(current_reserved_ICU_departures)
            departure_times[departure_index] = previous_departure_time
            temporary_reserved_departure_time_list.append(previous_departure_time)

            if waiting_queue and severity_level_list[waiting_queue[0][1]] == 3:
                _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)
                start_time = temporary_reserved_departure_time_list.pop(0)
                start_times[waiting_index] = start_time

                # Calculate departure time and add to ICU
                departure_time = start_time + length_of_stays[waiting_index] * 24
                departure_times[waiting_index] = departure_time
                heapq.heappush(current_reserved_ICU_departures, (departure_time, waiting_index))
            else:
                temporary_reserved_departure_time_list.pop(0)


        # Assign the current patient
        if len(current_regular_ICU_departures) < regular_capacity:
            start_time = arrival_time
            start_times[i] = start_time
            departure_time = start_time + length_of_stay
            departure_times[i] = departure_time
            heapq.heappush(current_regular_ICU_departures, (departure_time, i))
            #temporary_regular_departure_time_list = temporary_regular_departure_time_list[1:]

            

        elif severity == 3 and len(current_reserved_ICU_departures) < reserved_capacity:
            start_time = arrival_time
            start_times[i] = start_time
            departure_time = start_time + length_of_stay
            departure_times[i] = departure_time
            heapq.heappush(current_reserved_ICU_departures, (departure_time, i))
            #temporary_reserved_departure_time_list = temporary_reserved_departure_time_list[1:]


        else:
            heapq.heappush(waiting_queue, (-severity, severity, i))

    # Process remaining patients in the waiting queue
    current_time = arrival_times[-1]

    while waiting_queue:

        if severity_level_list[waiting_queue[0][1]] == 3:
            if current_regular_ICU_departures[0][0] <= current_reserved_ICU_departures[0][0]:
                earliest_available_time, departure_index = heapq.heappop(current_regular_ICU_departures)
                current_ICU_departures = current_regular_ICU_departures
            else:
                earliest_available_time, departure_index = heapq.heappop(current_reserved_ICU_departures)
                current_ICU_departures = current_reserved_ICU_departures

            _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)

            # Assign the bed to the patient in the waiting queue
            start_time = earliest_available_time
            start_times[waiting_index] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stays[waiting_index] * 24
            departure_times[waiting_index] = departure_time
            heapq.heappush(current_ICU_departures, (departure_time, waiting_index))
            # current_time = start_time
        else:
            earliest_available_time, departure_index = heapq.heappop(current_regular_ICU_departures) 
            _, waiting_severity, waiting_index = heapq.heappop(waiting_queue)

            # Assign the bed to the patient in the waiting queue
            start_time = earliest_available_time
            start_times[waiting_index] = start_time

            # Calculate departure time and add to ICU
            departure_time = start_time + length_of_stays[waiting_index] * 24
            departure_times[waiting_index] = departure_time
            heapq.heappush(current_regular_ICU_departures, (departure_time, waiting_index))
            # current_time = start_time






    return departure_times, start_times


def calculate_waiting_times(arrival_times, start_times):
    waiting_times = []

    for i in range(len(arrival_times)):
        waiting_time = start_times[i] - arrival_times[i]
        waiting_times.append(waiting_time)

    return waiting_times


def simultaneously_return(delta_arrival = 0,delta_length_of_stays=0.00, capacity=capacity, reserved_capacity=reserved_capacity):
    arrival_times, severity_level_list = simulate_arrival_process(delta_arrival=delta_arrival)
    length_of_stays = generate_length_of_stays(severity_level_list,average_length_of_stays=[days + delta_length_of_stays for days in average_length_of_stays])

    departure_times, start_times = simulate_departure_process_priority_with_reserved(arrival_times, severity_level_list, length_of_stays, capacity, reserved_capacity)
    waiting_times = calculate_waiting_times(arrival_times, start_times)

    return arrival_times, severity_level_list, start_times, departure_times, waiting_times



