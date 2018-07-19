import nengo
import numpy as np
import nengo_spa
import ev3_nengo.ev3link
import redis

# if not hasattr(ev3_nengo, 'link'):
#     ev3_nengo.link = ev3_nengo.ev3link.EV3Link('192.168.0.1')
# link = ev3_nengo.link

# print(link.dir('/sys/class/tacho-motor'))

# Class for graphics
class Environment(object):

    def __init__(self, size=10):
        self.size = size
        self._nengo_html_ = ''
        
    def __call__(self, t, value):
        mouth = value.squeeze()
        print(value)
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
        
        
        # # teeth
        # teeth_length = 2
        # teeth_val = mouth_base +(teeth+1)/2*teeth_length
        # self._nengo_html_ += '''
        # <polygon points="3,{mBase} 3.5,{tVal} 4,{mBase} " style="fill:white;" />
        # '''.format(tVal=teeth_val, mBase=mouth_base)
        
        # self._nengo_html_ += '''
        # <polygon points="4,{mBase} 4.5,{tVal} 5,{mBase} " style="fill:white;" />
        # '''.format(tVal=teeth_val, mBase=mouth_base)
        
        # self._nengo_html_ += '''
        # <polygon points="5,{mBase} 5.5,{tVal} 6,{mBase} " style="fill:white;" />
        # '''.format(tVal=teeth_val, mBase=mouth_base)
        
        # self._nengo_html_ += '''
        # <polygon points="6,{mBase} 6.5,{tVal} 7,{mBase} " style="fill:white;" />
        # '''.format(tVal=teeth_val, mBase=mouth_base)
        
        # # blush aka familiar
        # green_val = int(255 - (familiar +1)/2*(255-105)*0.7)
        # blue_val = int((familiar +1)/2*180*0.7)
        # self._nengo_html_ += '''
        # <circle cx="2" cy="5.5" r="1" fill="rgb(255,{gVal},{bVal})"/>
        # '''.format(gVal=green_val, bVal=blue_val)
        
        # self._nengo_html_ += '''
        # <circle cx="8" cy="5.5" r="1" fill="rgb(255,{gVal},{bVal})"/>
        # '''.format(gVal=green_val, bVal=blue_val)
        
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
    emotional_states = 4 # happy, distressed, sad, calm
    
    # percentage that current state vs. input affect your new state
    per_current_state = 1
    per_input = 2
    
    # inital emotional state -- starts in calm
    input_valence = 1
    input_arousal = -1
    
    
    # ---------------------- NUCLEI ---------------------------------------
    lateral = nengo.Ensemble(n_neurons=100,dimensions=input_stim_dim) # a sparse representation of the input
    basal = nengo.Ensemble(n_neurons=100,dimensions=emotion_dim)  # represents  current emotional state 
    central = nengo_spa.networks.selection.WTA(n_neurons=100, n_ensembles=emotional_states,
                                               threshold=0.3, 
                                               function=lambda x: 1 if x>0 else 0)
    PFC = nengo.Ensemble(n_neurons=100,dimensions=emotion_dim)
    
    
    # ---------------------- NODES ---------------------------------------------    
    
    # input stimuli
    low_stim= nengo.Node(input_stim_dim*[0])
    
    emotional_state = nengo.Node(lambda t: [input_valence,input_arousal] if t < 0.5 else [0,0], label='emotional state')
    
    #physio_response = nengo.Node(None,size_in=pysio_response_dim)
    
    
    
    # ------------------ CONNECTIONS --------------------------------------- 
        
    # input stim to lateral
    nengo.Connection(low_stim,lateral)
    
    input_data = [[-1],
                    [1],
                    [0.2],
                    [-0.2],
                    [0]]
                   
                    
    output_data = [[1,1],
                    [-1,1],
                    [0.5, -0.5],
                    [0.5, -0.5],
                    [0,0]
                    ]
                    

    # def joy2VA(x):
    #     return -1*x, x*x
    #nengo.Connection(lateral, basal, function=joy2VA)
    
    nengo.Connection(lateral, basal, eval_points=input_data, function=output_data,
                    scale_eval_points=False, transform =per_input)

    nengo.Connection(emotional_state, PFC)
    
    nengo.Connection(PFC,basal, transform=per_current_state)
    nengo.Connection(basal,PFC)
    
    emotion_matrix = np.array([
        [1, 1], # happy
        [-1, 1], # angry
        [-1, -1], # sad
        [1, -1], # calm
        ])
    
    nengo.Connection(basal, central.input, transform = emotion_matrix)
    #nengo.Connection(basal, central1, transform = emotion_matrix)
    #nengo.Connection(central1, central.input)

    def fast_reaction(x):
        joy = x
        
        happy = 0
        angry = 0
        sad = 0
        calm = 0
        
        if joy > 0.8:
            happy = 1
        elif joy < -0.8:
            sad = 1
        else:
            calm = 0.2
        
        return happy, angry, sad, calm
        
    nengo.Connection(lateral,central.input, function=fast_reaction)
    
    
    # outputs = np.array([
    #     # HR, breathing, sweating, adrenaline
    #     [0.2,     0,    0,  0.3],   # happy
    #     [1,       1,    1,  1],   # distressed
    #     [-0.3,     -0.3,    -0.3,   0],   # sad
    #     [-0.7, -0.7,  -0.7, 0],   # calm
    #     ])
    
    #nengo.Connection(central.output, physio_response, transform=outputs.T)
    
    import timeit
    now = timeit.default_timer()
    last_time = now
                    
    def run_away(t, x):
        global last_time
        happy, distressed, sad, calm = x
        output = 0
        
        if (happy > 0.6):
            output = 1
            
        if (sad > 0.6):
            output = -1
            
        now = timeit.default_timer()
        motor1 = 1
        motor2 = 2
        headMotor = 0
        # if now > last_time + 0.1:
        #     if (output > 0.6):
        #         # link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '100')
        #         # link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')
                
        #         # link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '100')
        #         # link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')
                
        #     elif(output < 0.2):
        #         # link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '-100')
        #         # link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')
                
        #         # link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '-100')
        #         # link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')
        #     else:
        #         link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor1, '0')
        #         link.write('/sys/class/tacho-motor/motor%d/command' % motor1, 'run-forever')
                
        #         link.write('/sys/class/tacho-motor/motor%d/speed_sp' % motor2, '0')
        #         link.write('/sys/class/tacho-motor/motor%d/command' % motor2, 'run-forever')
        #     last_time = now 
        #     link.write('/sys/class/tacho-motor/motor%d/speed_sp' % headMotor, '0')
        #     link.write('/sys/class/tacho-motor/motor%d/command' % headMotor, 'run-forever')
    
        return output
    
    # doing this because can't apply functions to passthrough nodes (central.output)
    movement = nengo.Node(size_in=4, output=run_away)
    nengo.Connection(central.output, movement)


    
    # ------------------- GRAPHICS ---------------------------------------
    input_env = nengo.Node(Environment(size=10), size_in=input_stim_dim, size_out=1)
    nengo.Connection(low_stim, input_env)
    
    #output_env = nengo.Node(Environment2(size=10), size_in=4, size_out=1)
    #nengo.Connection(physio_response, output_env)
    
    
