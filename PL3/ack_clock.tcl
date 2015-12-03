
if {$argc == 5} {
    set bandwidth [lindex $argv 0]
    set delay [lindex $argv 1]
    set qsize [lindex $argv 2] 
    set tcp_window [lindex $argv 3]
    set time [lindex $argv 4] 
} else {
    puts "    1Mb      bandwidth      1Mb" 
    puts "n0 ----- n1 ----------- n2 ----- n3"
    puts "    10ms      delay         10ms" 
    puts "Usage: ns $argv0 bandwidth delay queue_size tcp_window time"
    exit 1
}


# Create the 'Simulator' object
set ns [new Simulator]

# Open a file for writing the nam trace data
set trace_nam [open out.nam w]

$ns namtrace-all $trace_nam

# Add a 'finish' procedure that closes the trace and starts nam
proc finish {} {
    global ns trace_nam
    $ns flush-trace
    exec nam out.nam &
    exit 0
}

# Color Codes
$ns color 1 Red
$ns color 2 Green
$ns color 3 Blue

#############################################################################
####### YOUR CODE GOES BELOW THIS LINE ######################################

# Define the topology
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

#   object      from  to  bandwith   delay    queue
$ns duplex-link $n0   $n1 1Mb        10ms    DropTail
$ns duplex-link $n1   $n2 $bandwidth $delay  DropTail 
$ns duplex-link $n2   $n3 1Mb        10ms    DropTail


$ns duplex-link-op $n1 $n2 queuePos 0.5
$ns queue-limit $n1 $n2 $qsize 
set qmon [$ns monitor-queue $n1 $n2 1 2]

# Create a traffic source in node n0
    set ttcp0 [$ns create-connection TCP/RFC793edu $n0 TCPSink $n3 1]

$ttcp0 set window_ $tcp_window 

set ftp0 [new Application/FTP]
$ftp0 attach-agent $ttcp0


# Create a traffic sink in node n1
set null0 [new Agent/Null]
$ns attach-agent $n2 $null0

# When to start and to stop sending
$ns at 0.1 "$ftp0 start"
$ns at $time "finish"

####### END OF USER CODE ####################################################
#############################################################################

# Start the simulation
$ns run
