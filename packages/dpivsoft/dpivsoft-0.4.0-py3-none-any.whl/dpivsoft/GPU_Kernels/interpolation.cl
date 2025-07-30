KERNEL void Interpolation(GLOBAL_MEM float *output,
GLOBAL_MEM float *input,
GLOBAL_MEM int *x2,
GLOBAL_MEM int *y2,
GLOBAL_MEM int *x1,
GLOBAL_MEM int *y1,
GLOBAL_MEM int *data)
{
    int no_boxes_x = data[4];

    const SIZE_T i = get_global_id(0);

    int dx = x1[1]-x1[0];
    int dy = y1[no_boxes_x]-y1[0];

    int pos_x = (x2[i]-x1[0])/dx;
    int pos_y = (y2[i]-y1[0])/dy;

    int pos = pos_y*no_boxes_x+pos_x;

    if (pos_x < no_boxes_x){
        dx = x1[pos+1]-x1[pos];
    }
    else{
        dx = x1[pos]-x1[pos-1];
    }
    if (pos_y < no_boxes_x){
        dy = y1[pos+no_boxes_x]-y1[pos];
    }
    else{
        dy = y1[pos]-y1[pos-no_boxes_x];
    }

    float temp1 = (float)(x2[i]-x1[pos])/dx;
    float temp2 = (float)(y2[i]-y1[pos])/dy;

    output[i] = input[pos] * (1.0-temp1) * (1.0-temp2)
       + input[pos+1] * (temp1) * (1.0-temp2)
       + input[pos+1+no_boxes_x] * temp1 * temp2
       + input[pos+no_boxes_x] * (1.0-temp1) * (temp2);
}
