import nengo
import numpy as np
import ev3_nengo.ev3link
import redis

r = redis.StrictRedis(host='10.0.0.2',password='neuromorph')

if not hasattr(ev3_nengo, 'link'):
    ev3_nengo.link = ev3_nengo.ev3link.EV3Link('10.0.0.9')
link = ev3_nengo.link

print(link.dir('/sys/class/tacho-motor'))

# Class for graphics
class Environment(object):

    def __init__(self, size=10):
        self.size = size
        self._nengo_html_ = ''

    def __call__(self, t, value):
        mouth = value.squeeze()
        #print(value)
        eyes = 1
        #teeth = 1
        familiar = 1

        self._nengo_html_ = '<svg viewbox="0 0 10 10">'

        self._nengo_html_ += '''
        <circle cx="{x_pos}" cy="{y_pos}" r="{radius}" fill="{color}"/>
        '''.format(x_pos=5,y_pos=5,radius=5,color='yellow')

        # eye one
        self._nengo_html_ += '''
        <circle cx="{x_pos}" cy="{y_pos}" r="{radius}" fill="{color}"/>
        '''.format(x_pos=3.5,y_pos=3.5,radius=1,color='white')

        eye_size = (eyes+1)/2*0.2+0.4
        self._nengo_html_ += '''
        <circle cx="{x_pos}" cy="{y_pos}" r="{radius}" fill="{color}"/>
        '''.format(x_pos=3.5,y_pos=3.5,radius=eye_size,color='black')

        # eye two
        self._nengo_html_ += '''
        <circle cx="{x_pos}" cy="{y_pos}" r="{radius}" fill="{color}"/>
        '''.format(x_pos=6.5,y_pos=3.5,radius=1,color='white')

        self._nengo_html_ += '''
        <circle cx="{x_pos}" cy="{y_pos}" r="{radius}" fill="{color}"/>
        '''.format(x_pos=6.5,y_pos=3.5,radius=eye_size,color='black')

        # eyebrows
        eye_line1 = 2-(-1*eyes)*0.5
        if (eyes < 0):
            eye_line2 = 2+(-1*eyes)*0.5
        else:
            eye_line2 = 2+(eyes)*0.5
        self._nengo_html_ += '''
        <polyline points="2.5,{eVal1} 3,2 4,2 4.5,{eVal2}"
        style="fill:none;stroke:black;stroke-width:0.3" />
        '''.format(eVal1 = eye_line1, eVal2 = eye_line2)

        self._nengo_html_ += '''
        <polyline points="5.5,{eVal2} 6,2 7,2 7.5,{eVal1}"
        style="fill:none;stroke:black;stroke-width:0.3" />
        '''.format(eVal1 = eye_line1, eVal2=eye_line2)

        # mouth
        mouth_line = 8-(-1*mouth)*0.5
        mouth_base = 8-(mouth)*0.2
        self._nengo_html_ += '''
        <polyline points="3,{mVal} 4,{mBase} 6,{mBase} 7,{mVal}"
        style="fill:none;stroke:black;stroke-width:0.3" />
        '''.format(mVal = mouth_line, mBase = mouth_base)

        self._nengo_html_ += '</svg>'

        return 1

# ------------------------- OUTPUT GRAPHIC ------------------------
# Class for graphics
class Environment2(object):

    def __init__(self, size=10):
        self.size = size
        self._nengo_html_ = ''

    def __call__(self, t, value):
        heart, breathe, sweat, adrenaline = value

        self._nengo_html_ = '<svg viewbox="0 0 10 10">'

        # HR
        heart_color = (heart+1)/2
        h1 = 255-(255-65)*heart_color
        h2 = 255-(255-105)*heart_color
        h3 = 255-(255-255)*heart_color

        self._nengo_html_ += '''
        <circle cx="1.55" cy="2" r="1" fill="rgb({c1},{c2},{c3})"/>
        '''.format(c1=h1,c2=h2,c3=h3)

        self._nengo_html_ += '''
        <circle cx="3.45" cy="2" r="1" fill="rgb({c1},{c2},{c3})"/>
        '''.format(c1=h1,c2=h2,c3=h3)

        self._nengo_html_ += '''
        <polygon points=".53,2.2 2.5,5 4.47,2.2 " fill="rgb({c1},{c2},{c3})" />
        '''.format(c1=h1,c2=h2,c3=h3)

        # breathing
        lung_color = (breathe+1)/2
        c1_lung = 255-(255-0)*lung_color
        c2_lung = 255-(255-128)*lung_color
        c3_lung = 255-(255-0)*lung_color

        self._nengo_html_ += '''
        <polygon points="7.25,0 7.75,0 7.75,3 7.25,3 " fill="rgb({c1},{c2},{c3})" />
        '''.format(c1=c1_lung,c2=c2_lung,c3=c3_lung)

        self._nengo_html_ += '''
        <polyline points="7.5,2.6 6.5,3.6"
        style="fill:none;stroke:rgb({c1},{c2},{c3});stroke-width:0.5" />
        '''.format(c1=c1_lung,c2=c2_lung,c3=c3_lung)

        self._nengo_html_ += '''
        <polyline points="7.5,2.6 8.5,3.6"
        style="fill:none;stroke:rgb({c1},{c2},{c3});stroke-width:0.5" />
        '''.format(c1=c1_lung,c2=c2_lung,c3=c3_lung)

        self._nengo_html_ += '''
        <polygon points="6.7,2.5 6.7,4 6,4.7 5,5 5.7,2.1 " fill="rgb({c1},{c2},{c3})" />
        '''.format(c1=c1_lung,c2=c2_lung,c3=c3_lung)

        self._nengo_html_ += '''
        <polygon points="8.3,2.5 8.3,4 9,4.7 10,5 9.3,2.1 " fill="rgb({c1},{c2},{c3})" />
        '''.format(c1=c1_lung,c2=c2_lung,c3=c3_lung)

        # drop of water
        sweat_color = (sweat+1)/2
        c1 = 255;
        c2 =255 - (255-100)*sweat_color
        c3 = 255 - (255-0)*sweat_color

        self._nengo_html_ += '''
        <circle cx="2.5" cy="8.8" r="1.2" fill="rgb({color1},{color2},{color3})"/>
        '''.format(color1=c1, color2=c2, color3=c3)

        self._nengo_html_ += '''
        <polygon points="1.4,8.3 2.5,6 3.6,8.3 " fill="rgb({color1},{color2},{color3})" />
        '''.format(color1=c1, color2=c2, color3=c3)

        # adrenaline
        #arm_color = (adrenaline+1)/2
        arm_color=1;
        arm_muscle = (adrenaline+1)/2

        self._nengo_html_ += '''
        <circle cx="9" cy="9" r="1" fill="rgb({color1},{color2},{color3})"/>
        '''.format(color1=255-arm_color*(255-219),
        color2=255-arm_color*(255-112), color3=255-arm_color*(255-147))

        self._nengo_html_ += '''
        <polygon points="9,9.5 9,10 5,10 5,9.5 " fill="rgb({color1},{color2},{color3})" />
        '''.format(color1=255-arm_color*(255-219),
        color2=255-arm_color*(255-112), color3=255-arm_color*(255-147))

        self._nengo_html_ += '''
        <polyline points="5,10 6.5,6"
        style="fill:none;stroke:rgb({color1},{color2},{color3});stroke-width:0.5" />
        '''.format(color1=255-arm_color*(255-219),
        color2=255-arm_color*(255-112), color3=255-arm_color*(255-147))

        self._nengo_html_ += '''
        <ellipse cx="7" cy="6" rx=".8" ry=".5"
        style="fill:rgb({color1},{color2},{color3})" />
        '''.format(color1=255-arm_color*(255-219),
        color2=255-arm_color*(255-112), color3=255-arm_color*(255-147))

        self._nengo_html_ += '''
        <ellipse cx="6.8" cy="9.5" rx="1.4" ry="{arm_size}"
        style="fill:rgb({color1},{color2},{color3})" />
        '''.format(color1=255-arm_color*(255-219),
        color2=255-arm_color*(255-112), color3=255-arm_color*(255-147),
        arm_size=0.5+arm_muscle*1)


        self._nengo_html_ += '</svg>'

        return 1

# ----------------------------------------------------------------
model = nengo.Network()
with model:

    pysio_response_dim = 4 # HR, breathing, sweating, adrenaline
    input_stim_dim = 1 # joy
    emotion_dim = 2 # valence and arousal
    emotional_states = 3 # happy, distressed, calm

    # percentage that current state vs. input affect your new state
    per_current_state = 1
    per_input = 2

    # inital emotional state -- starts in calm
    input_valence = 1
    input_arousal = -1


    # ---------------------- Comms to Neuromorphic Hardware ---------------------------------------
    def lateral_2_redis(t,x):
        global r
        r.set('lateral_in',x[0])
        return
    def lat_redis_2_central(t):
        global r
        try:
            lfr2c0 = float(r.get('lateral_2_central_0'))
            lfr2c1 = float(r.get('lateral_2_central_1'))
            lfr2c2 = float(r.get('lateral_2_central_2'))
        except:
            lfr2c0 = lfr2c1 = lfr2c2 = 0
        return [lfr2c0, lfr2c1, lfr2c2]
    def lat_redis_2_basal(t):
        global r
        try:
            lfr2b0 = float(r.get('lateral_2_basal_0'))
            lfr2b1 = float(r.get('lateral_2_basal_1'))
        except:
            lfr2b0 = lfr2b1 = 0
        return [lfr2b0, lfr2b1]
    lateral_in_redis = nengo.Node(lateral_2_redis, size_in=1)
    lateral_redis_central = nengo.Node(lat_redis_2_central, size_out=3)
    lateral_redis_basal = nengo.Node(lat_redis_2_basal, size_out=2)

    def basal_2_redis(t,x):
        global r
        r.set('basal_in_0',x[0])
        r.set('basal_in_1',x[1])
        return
    def basal_from_redis(t):
        global r
        try:
            bfr0 = float(r.get('basal_out_0'))
            bfr1 = float(r.get('basal_out_1'))
            bfr2 = float(r.get('basal_out_2'))
        except:
            bfr0 = bfr1 = bfr2 = 0
        basal_output = [bfr0, bfr1, bfr2]
        return basal_output
    basal_in_redis = nengo.Node(basal_2_redis, size_in=2)
    basal_out_redis = nengo.Node(basal_from_redis, size_out=3)

    def central_2_redis(t,x):
        global r
        r.set('WTA_in_0',x[0])
        r.set('WTA_in_1',x[1])
        r.set('WTA_in_2',x[2])
        return
    def central_from_redis(t):
        global r
        try:
            cfr0 = float(r.get('WTA_out_0'))
            cfr1 = float(r.get('WTA_out_1'))
            cfr2 = float(r.get('WTA_out_2'))
        except:
            cfr0 = cfr1 = cfr2 = 0
        movement_vec = [cfr0, cfr1, cfr2]
        return movement_vec
    central_in_redis = nengo.Node(central_2_redis, size_in=3)
    central_out_redis = nengo.Node(central_from_redis, size_out=3)

    # ---------------------- Input Stimulus-------------------------------------

    # input stimuli
    def redis_input_func (t,x):
        global r
        
        try:
            amy_joy = float(r.get('AmyJoyScore'))
        except:
            amy_joy = 0
        return amy_joy

    low_stim = nengo.Node(redis_input_func, size_in=1)

    # ------------------ CONNECTIONS ---------------------------------------

    # input stim to lateral
    nengo.Connection(low_stim,lateral_in_redis)

    nengo.Connection(lateral_redis_basal, basal_in_redis)
    
    nengo.Connection(basal_out_redis, central_in_redis)

    nengo.Connection(lateral_redis_central, central_in_redis)



    import timeit
    now = timeit.default_timer()
    last_time = now

    def run_away(t, x):
        global last_time
        happy, distressed, calm = x
        output = 0

        max_emote = np.max([happy, distressed, calm])
        if max_emote == happy:
            output = 1
        elif max_emote == distressed:
            output = -1
        else:
            output = 0

        now = timeit.default_timer()
        motor1 = 0
        motor2 = 1
        if now > last_time + 0.1:
            if (output > 0.2):
                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '100')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')

                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '100')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')

            elif(output < -0.2):
                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '-100')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')

                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '-100')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')
            else:
                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '0')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')

                link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '0')
                link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')
            last_time = now

        return output

    # doing this because can't apply functions to passthrough nodes (central.output)
    movement = nengo.Node(size_in=3, output=run_away)

    nengo.Connection(central_out_redis, movement)

    # ------------------- GRAPHICS ---------------------------------------
    input_env = nengo.Node(Environment(size=10), size_in=input_stim_dim, size_out=1)
    nengo.Connection(low_stim, input_env)
    