from genomeview.track import Track

class Interval:
    def __init__(self, id_, chrom, start, end, strand="+", label=None):
        self.chrom = chrom
        self.start = start
        self.end = end
        self.id = id_
        self.label = label
        
        if isinstance(strand, bool):
            strand = {True:"+", False:"-"}[strand]
        self.strand = strand


class IntervalTrack(Track):
    def __init__(self, intervals):
        super().__init__()
        self.rows = []
        self.intervals_to_rows = {}
        
        self.row_height = 8
        self.margin_x = 15
        self.margin_y = 2
        self.label_distance = 3
        
        self.intervals = intervals

    def layout_interval(self, interval, label=None):
        row = 0
        interval_start = self.scale.topixels(interval.start)
        for row, row_end in enumerate(self.rows):
            if interval_start > row_end:
                break
        else:
            self.rows.append(None)
            row = len(self.rows) - 1
        
        new_end = self.scale.topixels(interval.end) + self.margin_x
        if label is not None:
            new_end += len(label) * self.row_height * 0.75
        self.rows[row] = new_end

        self.intervals_to_rows[interval.id] = row
        

    def layout(self, scale):
        super().layout(scale)
        
        # for chrom_part in scale.chrom_parts_collection:
        for interval in self.intervals:
            self.layout_interval(interval, getattr(interval, "label", None))
            
        self.height = (len(self.rows)+1) * (self.row_height+self.margin_y)
    
    def draw_interval(self, renderer, interval, label=None):
        start = self.scale.topixels(interval.start)
        end = self.scale.topixels(interval.end)
        
        row = self.intervals_to_rows[interval.id]
        top = row*(self.row_height+self.margin_y)
        
        color = "purple"
        if interval.strand == "-":
            color = "red"
        temp_label = label
        if label is None:
            temp_label = "{}_{}".format(interval.id, 1 if interval.read.is_read1 else 2)
        yield from renderer.rect(start, top, end-start, self.row_height, fill=color, **{"stroke":"none", "id":temp_label})
        if label is not None:
            yield from renderer.text(end+self.label_distance, top+self.row_height, label, anchor="left")
        
    def render(self, renderer):
        for interval in self.intervals:
            yield from self.draw_interval(renderer, interval, getattr(interval, "label", None))