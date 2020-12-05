## Observed behaviour

Describe in general words the observed behaviour of each of these servers and 
how it affects the video playback experience. Then explain what you believe is
happening and what is causing the described behaviour.

* FUNKY A: The video is not as good quality. The difference is minimal.

* FUNKY B: The video quality is worse and the video also lags/stutters - skips a few frames here and there. We believe this is happening because the server is not sending all the frames from the video.

* FUNKY C: The video both lags and is also accelerated sometimes. We believe this is happening because there are times no packets arrive from server and other times we have a burst of packets arriving at the same time.

* FUNKY D: The video lags alot and also some frames also seem to be skiped; lags/stutters more than FUNKY B. We believe this is happening because some frames are played out of order; packets with a higher sequence number arrived first and is therefore played first.

* FUNKY E: The video is fast forwarded. We believe this is happening a lot of packets are arriving very close to each other with not much delay. 

* FUNKY F: the video is very slow and is pretty much playing in slow motion. We believe this is happening because packets are arriving at a slow and consistent rate. Consistent because there are no stutters or lags.

* FUNKY G: the video is even slower than FUNKY F and seems to be skipping some frames as well. We believe this is happening because packets are arriving at an even slower rate and some packets are missing.

* FUNKY H: the video sometimes stutters for a moment and then speeds up for the next few seconds. This is pretty much the combination of all the previous behaviours we have seen so far. We believe this is happening because 


## Statistics

You may add additional columns with more relevant data.

| FUNKY SERVER | FRAME RATE (pkts/sec) | PACKET LOSS RATE (/sec) | OUT OF ORDER |
|:------------:|-----------------------|-------------------------|--------------|
|      A       |  22.3070              |   1.76                  |   0          |
|      B       |  15.2280              |   6.58                  |   0          |
|      C       |  25.0290              |   0.00                  |   1          |
|      D       |  12.5591              |   6.45                  |   1          |
|      E       |  59.1038              |   9.82                  |   0          |
|      F       |  10.1205              |   0.00                  |   0          |
|      G       |  7.83546              |   1.47                  |   0          |
|      H       |  24.9940              |   0.00                  |   0          |
|   REGULAR    |  25.0574              |   0.00                  |   0          |


## Result of analysis

Explain in a few words what you believe is actually happening based on the statistics above.

* FUNKY A: Some of the frames are missing randomly. This has frame rate of 22 pkts/sec compared to regular's 25 pkts/sec. In our original hypothesis we didn't mention anything about some of the frames missing. The data we gathered, specifically the frame rate, helped determine the behaviour of FUNKY A, which is missing frames.

* FUNKY B: More of the frames are missing and the delays are consistent with the missing frames. In our original hypothesis we mentioned the server is not sending all the frames. This is indeed true as we see that this server has a frame rate of 15 pkts/sec. In our program, we also printed out the sequence number of the arrived packets and the numbers do not increment by 1 in multiple instances, indicating missing packets.

* FUNKY C: Packets are missing, coming out of order, and do not arrive on the 40ms intervals. In our original hypothesis we did not mention about packets coming in, out of order. In our program we printed out the sequence number of the arriving packets and noticed there are multiple instances where packets are out of order. This explains the stutter-y behaviour seen in the playback experience.

* FUNKY D: Packets are missing, coming out of order, and do not arrive on the 40ms intervals. In our original hypothesis we mentioned the arriving packets are out of order. We were able to redefine our explanation by printing out the sequence number of the packets and the order they arrived, as well as the frame rate to determine that packets are missing.

* FUNKY E: Packets are sent to client at a rate much faster than 25 times per second. The frame rate for this server is close to 60 pkts/sec. In our original hypothesis we did mention the packets arrive very close together. A better explanation would be that packets arrive at a much faster rate.

* FUNKY F: Packets are sent to client at a rate much slower than 25 times per second. The frame rate for this server is about 10 pkts/sec. In our original hypothesis we mentioned the rate is consistent. This is further proven by the fact that no packets are out of order from the additional data we gathered.

* FUNKY G: Packets are sent to client at a rate much slower than 25 times per second, and some packets are missing. We know packets are missing because of the packet loss rate. We have the same explanation here as our original hypothesis.

* FUNKY H: Packets do not arrive on the 40ms intervals. In the ideal world, server will be sending a packet to the client every 40ms. When the video stutters, the time lapsed that we calculated is smaller than 40ms, indicating that packets do not arrive on the 40ms intervals.

