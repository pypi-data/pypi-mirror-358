import cv2
import numpy as np
import math
import inspect
class ShapeLab:
    def __init__(self, width=1000, height=700, background_color=(255, 255, 255)):
        """
        Initialize a new canvas with specified width, height, and background color.
        
        Parameters:
        width (int): Width of the canvas in pixels.
        height (int): Height of the canvas in pixels.
        background_color (tuple): BGR color for the background.
        """
        self.background_color = np.array(background_color, dtype=np.uint8)
        self.canvas = np.full((height, width, 3), self.background_color, dtype=np.uint8)
        self.history = []
        self.redo_stack = []
        self.batch_mode = False
    def clear(self):
        """
        Clears the canvas by resetting it to the current background color.
        """
        self.canvas[:, :] = self.background_color
    def save(self, filename):
        """
        Saves the current canvas image to a file.
        
        Parameters:
            filename (str): Path where the image should be saved.
        """
        cv2.imwrite(filename, self.canvas)
    def set_background(self, color):
        self.background_color=np.array(color, dtype=np.uint8)
        self.canvas=np.full_like(self.canvas, self.background_color)
        self.history.clear()
    def begin_batch(self):
        """
        Starts batch drawing mode. Undo history is saved only once during batch.
        """
        self.batch_mode = True
        self.backup()
    def end_batch(self):
        """
        Ends batch drawing mode. Drawing actions will now be tracked again individually.
        """
        self.batch_mode = False
    def backup(self):
        """
        Saves the current canvas state to the undo history if not in batch mode.
        """
        if not self.batch_mode:
            self.history.append(self.canvas.copy())
            self.redo_stack.clear()
            if len(self.history) > 20: 
                self.history.pop(0)
    def undo(self):
        """
        Reverts the canvas to the previous state, if available.
        """
        if self.history:
            self.redo_stack.append(self.canvas.copy())
            self.canvas = self.history.pop()
        else:
            print("No more undo steps available.")
    def redo(self):
        """
        Reapplies the last undone action, if available.
        """
        if self.redo_stack:
            self.history.append(self.canvas.copy())
            self.canvas = self.redo_stack.pop()
        else:
            print("No more redo steps available.")
    def  validate_color(self, color):
        """
        Validates if the given color is a valid BGR tuple or list.
        
        Parameters:
            color (tuple or list): The color to validate.
        """
        if not (isinstance(color, (tuple, list)) and len(color) == 3):
            raise ValueError("Color must be a 3-element tuple/list (B,G,R)")
        if not all(0 <= c <= 255 for c in color):
            raise ValueError("Color values must be 0-255")
    def  validate_coords(self, *points):
        """
        Ensures all provided points are within canvas bounds.
        
        Parameters:
            points (tuple): Points in (x, y) format.
        """
        h, w = self.canvas.shape[:2]
        for x, y in points:
            if not (0 <= x < w and 0 <= y < h):
                raise ValueError(f"Point ({x},{y}) outside canvas (0-{w-1}, 0-{h-1})")
    def validate_angle(self, angle):
        """
        Validates that the angle is numeric.
        
        Parameters:
            angle (int or float): Rotation angle in degrees.
        """
        if not isinstance(angle, (int, float)):
            raise TypeError("Angle must be numeric")
    def validate_thickness(self, thickness):
        """
        Validates thickness value for drawing.
        
        Parameters:
            thickness (int): Thickness in pixels or -1 for filled shape.
        """
        if not isinstance(thickness, int):
            raise TypeError("Thickness must be integer")
        if thickness != -1 and thickness < 1:
            raise ValueError("Thickness must be -1 (fill) or positive integer")
        
    @staticmethod
    def validate_inputs(func):
        """
        Decorator that validates common parameters such as color, thickness, angle,
        and coordinates before executing the shape drawing method.
        """
        def wrapper(self, *args, **kwargs):
            params = func.__code__.co_varnames[:func.__code__.co_argcount]
            bound = inspect.signature(func).bind(self, *args, **kwargs)
            bound.apply_defaults()
            if 'color' in bound.arguments:
                self.validate_color(bound.arguments['color'])
            if 'thickness' in bound.arguments:
                self.validate_thickness(bound.arguments['thickness'])
            if 'angle' in bound.arguments:
                self.validate_angle(bound.arguments['angle'])
            coordinate_params = ['start', 'end', 'center', 'pt1', 'pt2', 'pt3', 'pt4']
            for param in coordinate_params:
                if param in bound.arguments:
                    points = bound.arguments[param]
                    if isinstance(points, (tuple, list)) and len(points) == 2:
                        self.validate_coords(points)
            return func(self, *args, **kwargs)
        return wrapper
        
    @validate_inputs
    def line(self,start,end,color,thickness,auto_backup=True):
        """
        Draws a straight line between two points.
        
        Parameters:
            start (tuple): Starting coordinate (x, y).
            end (tuple): Ending coordinate (x, y).
            color (tuple): Line color in BGR.
            thickness (int): Thickness in pixels.
            auto_backup (bool): Whether to save canvas state before drawing.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        cv2.line(self.canvas,start,end,color=color,thickness=thickness)
    @validate_inputs
    def rectangle(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a rotated rectangle using two corner points.

        Parameters:
            start (tuple): One corner of the rectangle.
            end (tuple): Opposite corner.
            angle (float): Rotation in degrees.
            color (tuple): Color of rectangle.
            thickness (int): Border thickness or -1 to fill.
            auto_backup (bool): Save canvas state before drawing.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        pt1=(start[0],start[1])
        pt2=(end[0],start[1])
        pt3=(end[0],end[1])
        pt4=(start[0],end[1])
        rect=np.array([pt1,pt2,pt3,pt4],dtype=np.float32)
        angle_rad=math.radians(angle)
        rot_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in rect:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rot_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def circle(self,center,radius,color,thickness,auto_backup=True):
        """
        Draws a circle with specified center and radius.

        Parameters:
            center (tuple): Center of the circle.
            radius (int): Radius of the circle.
            color (tuple): Circle color.
            thickness (int): Border thickness or -1 for filled.
            auto_backup (bool): Save canvas state before drawing.
        """
        if not isinstance(radius, int) or radius <= 0:
            raise ValueError("Radius must be a positive integer")
        if auto_backup and not self.batch_mode:
            self.backup()
        cv2.circle(self.canvas,center,radius,color=color,thickness=thickness)
    @validate_inputs
    def triangle(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws an equilateral triangle within the bounding box defined by start and end.

        Parameters:
            start (tuple): Top-left coordinate.
            end (tuple): Bottom-right coordinate.
            angle (float): Rotation in degrees.
            color (tuple): Color of the triangle.
            thickness (int): Line thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        pt1=((start[0]+end[0])//2,min(start[1],end[1]))
        pt2=(min(start[0],end[0]),max(start[1],end[1]))
        pt3=(max(start[0],end[0]),max(start[1],end[1]))
        tria=np.array([pt1,pt2,pt3],np.float32)
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        angle_rad=math.radians(angle)
        rot_matrix=np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in tria:
            vec=np.array([x-center_x,y-center_y]) 
            rotated_vec=rot_matrix@vec 
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def right_triangle_rh(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a right-angled triangle with the right angle at the right-hand corner.

        Parameters:
            start (tuple): Top-left coordinate.
            end (tuple): Bottom-right coordinate.
            angle (float): Rotation angle.
            color (tuple): Color of the triangle.
            thickness (int): Border thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        pt1=(min(start[0],end[0]),min(start[1],end[1]))
        pt2=(min(start[0],end[0]),max(start[1],end[1]))
        pt3=(max(start[0],end[0]),max(start[1],end[1]))
        rtrh=np.array([pt1,pt2,pt3],np.float32)
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        rotated_pts=[]
        angle_rad=math.radians(angle)
        rot_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        for (x,y) in rtrh:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rot_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def right_triangle_lh(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a right-angled triangle with the right angle at the left-hand corner.

        Parameters:
            start (tuple): Top-left coordinate.
            end (tuple): Bottom-right coordinate.
            angle (float): Rotation angle.
            color (tuple): Shape color.
            thickness (int): Line thickness or -1 for fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        pt1=(max(start[0],end[0]),min(start[1],end[1]))
        pt2=(min(start[0],end[0]),max(start[1],end[1]))
        pt3=(max(start[0],end[0]),max(start[1],end[1]))
        rtlh=np.array([pt1,pt2,pt3],dtype=np.float32)
        rotated_pts=[]
        angle_rad=math.radians(angle)
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        rot_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        for (x,y) in rtlh:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rot_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def diamond(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a diamond shape inside the bounding box from start to end.

        Parameters:
            start (tuple): Top-left of the bounding box.
            end (tuple): Bottom-right of the bounding box.
            angle (float): Rotation angle in degrees.
            color (tuple): Color of diamond.
            thickness (int): Border thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        pt1=((start[0]+end[0])//2,min(start[1],end[1]))
        pt2=(min(start[0],end[0]),(start[1]+end[1])//2)
        pt3=(max(start[0],end[0]),(start[1]+end[1])//2)
        pt4=((start[0]+end[0])//2,max(start[1],end[1]))
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        diam=np.array([pt1,pt2,pt4,pt3],dtype=np.float32)
        angle_rad=math.radians(angle)
        rotation_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in diam:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotation_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def pentagon(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a regular pentagon rotated around its center.

        Parameters:
            start (tuple): Bounding box start point.
            end (tuple): Bounding box end point.
            angle (float): Rotation in degrees.
            color (tuple): Color of the pentagon.
            thickness (int): Thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        radius=min(width,height)//2
        points=[]
        for i in range(5):
            theta_deg=-90+i*(360/5)
            theta_rad=math.radians(theta_deg)
            x=center_x+radius*math.cos(theta_rad)
            y=center_y+radius*math.sin(theta_rad)
            points.append((x,y))
        points=np.array(points,np.float32)
        angle_rad=math.radians(angle)
        rotation_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotation_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def hexagon(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a regular hexagon inside the defined box.

        Parameters:
            start (tuple): Top-left of box.
            end (tuple): Bottom-right of box.
            angle (float): Rotation in degrees.
            color (tuple): Border/fill color.
            thickness (int): Border width or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        radius=min(width,height)//2
        points=[]
        for i in range(6):
            theta_deg=-90+i*(360/6)
            theta_rad=math.radians(theta_deg)
            x=center_x+radius*math.cos(theta_rad)
            y=center_y+radius*math.sin(theta_rad)
            points.append((x,y))
        points=np.array(points,dtype=np.float32)
        angle_rad=math.radians(angle)
        rotation_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotation_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def heptagon(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a regular heptagon (7 sides).

        Parameters:
            start (tuple): Start of bounding box.
            end (tuple): End of bounding box.
            angle (float): Rotation angle.
            color (tuple): Color of heptagon.
            thickness (int): Border thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        radius=min(width,height)//2
        points=[]
        for i in range(7):
            theta_deg=-90+i*(360/7)
            theta_rad=math.radians(theta_deg)
            x=center_x+radius*math.cos(theta_rad)
            y=center_y+radius*math.sin(theta_rad)
            points.append((x,y))
        angle_rad=math.radians(angle)
        rotation_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotation_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def octagon(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a regular octagon (8 sides) within the box.

        Parameters:
            start (tuple): Top-left point of box.
            end (tuple): Bottom-right point of box.
            angle (float): Rotation angle.
            color (tuple): BGR color of shape.
            thickness (int): Border thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        radius=min(width,height)//2
        points=[]
        for i in range(8):
            theta_deg=-90+i*(360/8)
            theta_rad=math.radians(theta_deg)
            x=center_x+radius*math.cos(theta_rad)
            y=center_y+radius*math.sin(theta_rad)
            points.append((x,y))
        angle_rad=math.radians(angle)
        rotated_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotated_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def square(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a square centered within the bounding box and rotates it.

        Parameters:
            start (tuple): First corner.
            end (tuple): Opposite corner.
            angle (float): Rotation.
            color (tuple): Color of square.
            thickness (int): Line thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        half_side=min(width,height)//2
        points=[]
        points=[
            (center_x-half_side,center_y-half_side), 
            (center_x+half_side,center_y-half_side), 
            (center_x+half_side,center_y+half_side), 
            (center_x-half_side,center_y+half_side) 
        ]
        angle_rad=math.radians(angle)
        rotated_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        rotated_pts=[]
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotated_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((int(rx),int(ry)))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def n_gon(self,start,end,n,angle,color,thickness,auto_backup=True):
        """
        Draws a regular polygon with n sides.

        Parameters:
            start (tuple): Top-left of bounding box.
            end (tuple): Bottom-right of bounding box.
            n (int): Number of sides.
            angle (float): Rotation in degrees.
            color (tuple): Shape color.
            thickness (int): Line thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        radius=min(width,height)//2
        points=[]
        for i in range(n):
            theta_deg=-90+i*(360/n)
            theta_rad=math.radians(theta_deg)
            x=center_x+radius*math.cos(theta_rad)
            y=center_y+radius*math.sin(theta_rad)
            points.append((x,y))
        rotated_pts=[]
        angle_rad=math.radians(angle)
        rotated_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotated_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((rx,ry))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def heart(self,start,end,angle,color,thickness,auto_backup=True):
        """
        Draws a heart shape centered within the bounding box.

        Parameters:
            start (tuple): Top-left of bounding box.
            end (tuple): Bottom-right of bounding box.
            angle (float): Rotation angle.
            color (tuple): Heart color.
            thickness (int): Line thickness or -1 to fill.
        """
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        scale=min(width,height)/32 
        t_vals=np.linspace(0,2*math.pi,200) 
        points=[]
        for t in t_vals:
            x=16*(math.sin(t)**3)
            y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
            px=center_x+int(x*scale)
            py=center_y-int(y*scale)
            points.append((px,py))
        rotated_pts=[]
        angle_rad=math.radians(angle)
        rotated_matrix=np.array([
            [math.cos(angle_rad),-math.sin(angle_rad)],
            [math.sin(angle_rad),math.cos(angle_rad)]
        ])
        for (x,y) in points:
            vec=np.array([x-center_x,y-center_y])
            rotated_vec=rotated_matrix@vec
            rx,ry=rotated_vec+np.array([center_x,center_y])
            rotated_pts.append((rx,ry))
        rotated_pts=np.array(rotated_pts,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[rotated_pts],color)
        else:
            cv2.polylines(self.canvas,[rotated_pts],isClosed=True,color=color,thickness=thickness)
    @validate_inputs
    def star(self,start,end,points,sharpness,angle,color,thickness,auto_backup=True):
        """
        Draws a customizable star shape.

        Parameters:
            start (tuple): Top-left of bounding box.
            end (tuple): Bottom-right of bounding box.
            points (int): Number of star points.
            sharpness (float): Ratio of inner to outer radius (0 < sharpness < 1).
            angle (float): Rotation angle in degrees.
            color (tuple): Star color.
            thickness (int): Line thickness or -1 to fill.
        """
        if not isinstance(points, int) or points < 2:
            raise ValueError("Star points must be integer ≥ 2")
        if not 0 < sharpness < 1:
            raise ValueError("Sharpness must be between 0 and 1")
        if auto_backup and not self.batch_mode:
            self.backup()
        center_x=(start[0]+end[0])//2
        center_y=(start[1]+end[1])//2
        width=abs(end[0]-start[0])
        height=abs(end[1]-start[1])
        outer_radius=min(width,height)//2
        inner_radius=outer_radius*sharpness
        total_points=points*2
        angle_offset=math.radians(angle)
        star_points=[]
        for i in range(total_points):
            radius=outer_radius if i%2==0 else inner_radius
            theta=-math.pi/2+i*((2*math.pi)/total_points)+angle_offset
            x=center_x+radius*math.cos(theta)
            y=center_y+radius*math.sin(theta)
            star_points.append((x,y))
        pts=np.array(star_points,dtype=np.int32).reshape(-1,1,2)
        if thickness==-1:
            cv2.fillPoly(self.canvas,[pts],color)
        else:
            cv2.polylines(self.canvas,[pts],isClosed=True,color=color,thickness=thickness)
    def launch_viewer(self):
        """
        Opens a window to display the current canvas.
        Press any key to close the window.
        """
        cv2.imshow("Canvas",self.canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
