#include <iostream>
using namespace std;

void SelectSort(int a[],int n) //选择排序
{
    int mix,temp;
    for(int i=0;i<n-1;i++) //每次循环数组，找出最小的元素，放在前面，前面的即为排序好的
    {
        mix=i; //假设最小元素的下标
        for(int j=i+1;j<n;j++) //将上面假设的最小元素与数组比较，交换出最小的元素的下标
            if(a[j]<a[mix])
                mix=j;
        //若数组中真的有比假设的元素还小，就交换
        if(i!=mix)
        {
            temp=a[i];
            a[i]=a[mix];
            a[mix]=temp;
        }
    }
}



int main()
{
    int a[10] = {43, 65, 4, 23, 6, 98, 2, 65, 7, 79};
    cout<<"选择排序："<<endl;
    SelectSort(a, 10);
    for(int i=0;i<10;i++)
        cout<<a[i]<<" ";
    cout<<endl;
    return 0;
}
