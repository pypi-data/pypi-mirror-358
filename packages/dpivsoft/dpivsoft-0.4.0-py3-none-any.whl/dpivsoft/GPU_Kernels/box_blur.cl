KERNEL void box_blur(GLOBAL_MEM float *output,
GLOBAL_MEM float *input,
GLOBAL_MEM int *data)
{
    int w = data[4];
    int h = data[5];

    const SIZE_T i = get_global_id(0);

    int pos_y = i/w;
    int pos_x = i%w;

    float sum = 0.0;
    int count = 0;

    for (int ky = -1; ky <= 1; ky++){
        for (int kx=-1;kx <=1; kx++){
            int nx = pos_x + kx;
            int ny = pos_y + ky;

            nx = max(0, min(nx, w-1));
            ny = max(0, min(ny, h-1));

            sum += input[ny*w+nx];
            count++;
            
        }
    }
    output[i] = sum/count;
}