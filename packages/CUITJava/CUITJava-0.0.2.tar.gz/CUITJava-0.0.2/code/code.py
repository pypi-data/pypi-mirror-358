题库 = {
    "网络服务器": """
    import java.io.*;
import java.net.*;

public class TCPServer {
    public static void main(String[] args) {
        final int PORT = 8888;
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("服务器启动，监听端口: " + PORT);
            
            while (true) {
                try (Socket clientSocket = serverSocket.accept();
                     BufferedReader in = new BufferedReader(
                         new InputStreamReader(clientSocket.getInputStream()));
                     PrintWriter out = new PrintWriter(
                         clientSocket.getOutputStream(), true)) {
                     
                    // 显示客户端连接信息
                    System.out.println("客户端连接: " + clientSocket.getInetAddress());
                    
                    // 读取客户端消息
                    String message = in.readLine();
                    System.out.println("收到客户端消息: " + message);
                    
                    // 发送响应
                    String response = "服务端已收到: " + message;
                    out.println(response);
                    System.out.println("已发送响应: " + response);
                    
                } catch (IOException e) {
                    System.err.println("客户端通信异常: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("服务器启动失败: " + e.getMessage());
        }
    }
}

    """,
    "网络客户端": """
    import java.io.*;
import java.net.*;

public class TCPClient {
    public static void main(String[] args) {
        final String SERVER_IP = "127.0.0.1";
        final int PORT = 8888;
        
        try (Socket socket = new Socket(SERVER_IP, PORT);
             PrintWriter out = new PrintWriter(
                 socket.getOutputStream(), true);
             BufferedReader in = new BufferedReader(
                 new InputStreamReader(socket.getInputStream()));
             BufferedReader stdIn = new BufferedReader(
                 new InputStreamReader(System.in))) {
            
            System.out.println("已连接到服务器...");
            
            // 读取用户输入
            System.out.print("请输入要发送的消息: ");
            String userInput = stdIn.readLine();
            
            // 发送消息到服务器
            out.println(userInput);
            System.out.println("已发送消息: " + userInput);
            
            // 接收服务器响应
            String response = in.readLine();
            System.out.println("服务器响应: " + response);
            
        } catch (UnknownHostException e) {
            System.err.println("未知主机: " + SERVER_IP);
        } catch (IOException e) {
            System.err.println("通信异常: " + e.getMessage());
        }
    }
}

    """,
    "数据库": """
    import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.sql.SQLException;

public class TeacherInfoQuery {

    // 数据库连接信息
    private static final String DB_URL = "jdbc:mysql://localhost:3306/school_db";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "password";

    public static void main(String[] args) {
        Connection conn = null;
        Statement stmt = null;
        ResultSet rs = null;

        try {
            // 1. 注册JDBC驱动
            Class.forName("com.mysql.cj.jdbc.Driver");
            
            // 2. 打开数据库连接
            conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            
            // 3. 创建Statement对象
            stmt = conn.createStatement();
            
            // 4. 执行SQL查询
            String sql = "SELECT name, age FROM teachers";
            rs = stmt.executeQuery(sql);
            
            // 5. 处理结果集
            System.out.println("+----------------------+-----+");
            System.out.println("| 教师姓名             | 年龄 |");
            System.out.println("+----------------------+-----+");
            
            while (rs.next()) {
                // 通过列名获取数据
                String name = rs.getString("name");
                int age = rs.getInt("age");
                
                // 格式化输出结果
                System.out.printf("| %-20s | %-3d |\n", name, age);
            }
            
            System.out.println("+----------------------+-----+");
            System.out.println("查询完成！共找到 " + getRowCount(rs) + " 位教师信息。");
            
        } catch (SQLException se) {
            // 处理JDBC错误
            se.printStackTrace();
        } catch (Exception e) {
            // 处理Class.forName错误
            e.printStackTrace();
        } finally {
            // 6. 关闭资源
            try {
                if (rs != null) rs.close();
            } catch (SQLException se2) {
                // 忽略关闭错误
            }
            try {
                if (stmt != null) stmt.close();
            } catch (SQLException se2) {
                // 忽略关闭错误
            }
            try {
                if (conn != null) conn.close();
            } catch (SQLException se) {
                se.printStackTrace();
            }
        }
    }
    
    // 获取结果集行数
    private static int getRowCount(ResultSet rs) {
        try {
            int currentRow = rs.getRow();
            rs.last();
            int rowCount = rs.getRow();
            rs.beforeFirst();
            if (currentRow == 0) {
                // 如果当前在第一行之前
                rs.next();
            }
            return rowCount;
        } catch (SQLException e) {
            e.printStackTrace();
            return 0;
        }
    }
}

    """,
    "判断题": """Java题目及正确答案整理
1-1
题目： 线程的优先级一定是线程的执行顺序。
答案： F
1-2
题目： static关键字可以修饰成员变量，也可以修饰局部变量。
答案： F
1-3
题目： 子类如果想使用父类的构造方法，必须在子类的构造方法中使用，并且必须使用关键字super来表示，而且super必须是子类构造方法中的头一条语句。
答案： T
1-4
题目： Java语言中，变量名可以用汉字表示，但建议尽量不这样操作。
答案： T
1-5
题目： 构造方法可以调用本类中重载的构造方法和它的父类的构造方法。
答案： T
1-6
题目： 每个Java程序最少有一个执行线程。当运行程序的时候, JVM运行负责调用main()方法的执行线程。
答案： T
1-7
题目： 文件缓冲流的作用是提高文件的读/写效率。
答案： T
1-8
题目： 对象序列化是指将一个Java对象转换成一个I/O流中的字节序列的过程。
答案： T
1-9
题目： BufferedInputStream和BufferedOutputStream不是字节缓冲流。
答案： F
1-10
题目： InputStream类中的close()方法是用于关闭流并且释放流所占的系统资源。
答案： T
1-11
题目： 在java.util.Set接口的实现类java.util.HashSet所表示的集合中，元素是无序的并且不允许重复
答案： T
1-12
题目： 在java.util.List接口的实现类java.util.ArrayList所表示的集合中，元素是有序的并且可以重复。该数据结构底层由数组来实现，能够精确地控制每个元素的插入位置，或者删除某个位置的元素，对元素的随机访问速度特别快。
答案： T
1-13
题目： 在Collection集合中元素类型必须是相同的。
答案： F
1-14
题目： 字符串缓冲区类允许在当前对象上进行追加、增加、删除、修改字符的操作。而字符串对象不具备这一特点，只要改变就生成一个新的对象。
答案： T
1-15
题目： 一个异常处理中 finally语句块可以不出现，也可以出现一次。
答案： T
1-16
题目： 若异常发生时，没有捕获，后续的程序不受任何影响，依然能正常执行。
答案： F
1-17
题目： 一个类如果实现一个接口，那么它就需要实现接口中定义的全部方法，否则该类必须定义成抽象类。
答案： T
1-18
题目： 当成员变量（属性）的访问权限不足时，可以通过增加公开的set方法和get方法对属性进行设置值或获取值来进行访问。
答案： T
1-19
题目： 实例变量是属于对象的。一个类的多个对象对实例变量可以设置不同的值。
答案： T
1-20
题目： 多线程是指将CPU资源按时间片分配到多个任务上，看似并行工作，实质上在同一时刻只有一个线程在工作；在一段时间之内，是多个线程在同时工作。
答案： T
1-21
题目： Java允许创建不规则数组，即Java多维数组中各行的列数可以不同。
答案： T
1-22
题目： 声明为final的方法不能在子类中被覆盖。
答案： T
1-23
题目： 类及其属性、方法可以同时有一个以上的修饰符来修饰。
答案： T
1-24
题目： 在异常处理中，若try中的代码可能产生多种异常则可以对应多个catch语句，若catch中的参数类型有父类子类关系，此时应该将父类放在前面，子类放在后面。
答案： F
1-25
题目： Java中数组的元素可以是简单数据类型的量，也可以是某一类的对象。
答案： T
1-26
题目： Java基本数据类型的变量所占存储空间大小是固定的，与平台（操作系统）无关。这样方便程序的移植。
答案： T
1-27
题目： Java虚拟机可以将类文件（.class）在不同的操作系统上运行，从而实现跨平台特性。
答案： T
1-28
题目： public可以修饰类和类的成员，但private只能修饰类的成员和内部类，不能修饰类。
答案： T
1-29
题目： Java中使用java.util.Scanner类的对象进行输入字符串时，使用其next方法或者nextLine方法都能取得字符串，二者没有什么差别。
答案： F
1-30
题目： 在Java中,类只是一种抽象的数据类型，程序中一般使用的是由该类创建的对象。
答案： T
1-31
题目： 子类重写的方法可以拥有比父类方法更加严格的访问权限。
答案： F
1-32
题目： 不存在继承关系的情况下，也可以实现重写。
答案： F
1-33
题目： 构造方法不可以被继承。
答案： T
1-34
题目： JAVA中，一个接口允许继承多个接口。
答案： T
1-35
题目： 在JAVA的集合框架中，Map接口是自Collection接口继承而来。
答案： F
1-36
题目： 由于UDP是面向无连接的协议，可以保证数据的完整性，因此在传输重要数据时建议使用UDP协议。
答案： F
1-37
题目： 当我们创建一个线程对象时，该对象表示的线程就立即开始运行。
答案： F
1-38
题目： 一个新线程创建后会自动进入就绪状态，等待CPU的调度。
答案： F
1-39
题目： Java源文件中只能有一个类。
答案： F
1-40
题目： java源文件的扩展名是.class。
答案： F
1-41
题目： Java中通过关键字new创建一个类的实例对象。
答案： T
1-42
题目： Java中使用package定义包，使用import导入包。
答案： T
1-43
题目： Java中不可以自定义异常。
答案： F
1-44
题目： Java使用throw和throws来捕获异常。
答案： F
1-45
题目： 匿名内部类不能有构造方法，不能定义任何静态成员、方法和类，只能创建匿名内部类的一个实例。
答案： T
1-46
题目： Java线程有新建、就绪、运行、睡眠、等待、阻塞、死亡等状态。
答案： T
1-47
题目： 线程调用sleep()结束后，立即恢复执行。
答案： F
1-48
题目： super()和this()只能在构造方法中调用。
答案： T
1-49
题目： 当线程类所定义的run()方法执行完毕，线程的运行就会终止。
答案： T
1-50
题目： StringBuffer类创建的字符串长度是固定的。
答案： F
1-51
题目： 新建状态的线程被start()后，将进入线程队列等待CPU时间片，处于运行状态。
答案： F
1-52
题目： 在Java中，高优先级的可运行线程一定会抢占低优先级线程。
答案： F
1-53
题目： 系统自动引入java.lang包中的所有类，因此不需要再显式地使用import语句引入该包的所有类。
答案： T
1-54
题目： 数组作为方法的参数时，必须在数组名后加方括号。
答案： F
1-55
题目： 使用方法length( )或length属性可以获得字符串或数组的长度。
答案： F
1-56
题目： Java的字符类型采用的是ASCII编码。
答案： F
1-57
题目： 构造函数名应与类名相同，返回类型为void。
答案： F
1-58
题目： 一个数组可以存放不同类型的数值。
答案： F
1-59
题目： 在Java程序中，可以使用protected来修饰一个类。
答案： F
1-60
题目： java语言中不用区分字母的大写小写。
答案： F
1-61
题目： 可以使用throws语句来指明方法有异常抛出。
答案： T
1-62
题目： 可以使用throw语句来抛出异常。
答案： T
1-63
题目： 引用一个类的属性或调用其方法，必须以这个类的对象为前缀。
答案： F
1-64
题目： package语句必须放到java程序的最开始。
答案： T""",
    "选择题": """
    2-1
题目：关于TCP 和UDP协议，下列说法错误的是
答案：使用UDP传输数据时，发送方所发送的数据报以相同的次序到达接收方

2-2
题目：以下关于异常的说法正确的是。
答案：可能抛出系统异常的方法是不需要声明异常的

2-3
题目：当线程调用start()后，其所处状态为。
答案：就绪状态

2-4
题目：欲构造ArrayList类的一个实例，此类继承了List接口，下列正确的方法是。
答案：List myList = new ArrayList();

2-5
题目：对于catch子句的排列，下列哪种是正确的。
答案：子类在先，父类在后

2-6
题目：下列哪个情况可以终止当前线程的运行？
答案：抛出一个异常时

2-7
题目：关于异常(Exception)，下列描述错误的是
答案：异常必须在内部自己处理，不能抛给外层的程序进行处理

2-8
题目：如果在关闭Socket时发生一个I/O错误，会抛出（ ）。
答案：IOException

2-9
题目：以下哪个选项最准确地描述synchronized关键字？
答案：保证在某时刻只有一个线程可访问方法或对象

2-10
题目：下面描述中正确的是？
答案：子类无法继承父类的构造方法

2-11
题目：Java中，下面是有关子类及父类构造方法的描述,其中正确的是？
答案：子类必须通过super关键字调用父类的构造方法

2-12
题目：线程整个生命周期可以分为五个阶段，以下哪个不属于其生命周期（）
答案：生存状态

2-13
题目：进程和线程的关系--下面关于进程和线程的关系不正确的是？
答案：线程之间不共享进程中的共享变量和部分环境

2-14
题目：UDP通信--进行UDP通信时，在接收端若要获得发送端的IP地址，可以使用DatagramPacket的（ ）方法。
答案：getAddress()

2-15
题目：文件读写--字符流与字节流读写数据的区别在于（ ）。
答案：每次读写数据的组织单位不同

2-16
题目：如下代码，程序的输出结果将是：（ ）。
答案：11 12
20 12

2-17
题目：定义一个Java类时，如果前面使用关键字（ ）修饰，那么该类不可以被继承。
答案：final

2-18
题目：类成员修饰词--下列关于修饰符使用的说法，错误的是（ ）。
答案：static方法中能访问非static的属性

2-19
题目：下面的描述中，哪一种是Java的垃圾自动回收机制所回收的对象（ ）？
答案：未被任何变量指向的对象

2-20
题目：下面选项中不是开发Java程序的步骤（ ）
答案：发布

2-21
题目：对JDK描述错误的是（ ）。
答案：JDK本身也是平台无关的，不同的操作系统安装的JDK是一样的

2-22
题目：Java语言中的运行机制是什么？
答案：编译和解释型

2-23
题目：在Java中，以下程序段的输出结果是 （）。
答案：27

2-24
题目：以下二维数组的定义正确的是（ ）
答案：int a[][] = new int[3][];

2-25
题目：以下哪句是错误的？
答案：import是把要import的类的源代码插入到import语句所在的地方

2-26
题目：在windows平台上安装配置JDK时，下列的说法错误的是_____。
答案：javac的功能是编译并执行 java代码项

2-27
题目：一个*.java文件中可以包含多少个public类？
答案：最多1个

2-28
题目：将以下哪种方法插入行6是不合法的。
答案：public int aMethod（int a，int b）throws IOException { }

2-29
题目：非静态内部类，有时也称为实例内部类或成员内部类，它具有以下特点，除了（ ）。
答案：在创建非静态内部类的实例时，外部类的实例不是必须存在

2-30
题目：下面哪个流类属于面向字符的输入流( ) 。
答案：InputStreamReader

2-31
题目：下列关于线程优先级的说法中，正确的是
答案：在创建线程后的任何时候都可以设置线程优先级

2-32
题目：Java中关于对象成员占用内存的说法哪个正确？
答案：同一个类的对象使用不同的内存段，但静态成员共享相同的内存空间

2-33
题目：下列语句中能够实现判断列表中是否存在字符串“小说”的是？
答案：bookTypeList.contains("小说");

2-34
题目：要从文件"file.dat"中读出第10个字节到变量C中，以下合适的代码段是？
答案：FileInputStream in=new FileInputStream("file.dat");
in.skip(9);
int c=in.read();

2-35
题目：子类覆盖父类静态方法，程序执行的结果是：（ ）。
答案：Child.test()
Base.test()

2-36
题目：假设 int x=4，y=100，循环体共执行了多少次?
答案：2次

2-37
题目：关于private访问权限说法有误的是
答案：private修饰的方法，在其子类中可以通过对象访问

2-38
题目：关于接口与abstract的说法，不正确的是。
答案：abstract类中方法可以不实现，接口中的方法必须实现

2-39
题目：在一个Java文件中，使用import、class和package的正确顺序是？
答案：package、import、class

2-40
题目：以下哪个关键字可以用来为对象加互斥锁？
答案：synchronized

2-41
题目：一个线程可以由下列哪种状态直接到达运行状态？
答案：就绪状态

2-42
题目：下面哪个Set是根据内容排序的？
答案：TreeSet

2-43
题目：有关线程的哪些叙述是对的?
答案：使用start()方法可以使一个线程成为可运行的，但是它不一定立即开始运行

2-44
题目：访问修饰符作用范围由大到小是（ ）
答案：public-protected-default-private

2-45
题目：ServerSocket的accept()方法返回的对象类型是
答案：Socket

2-46
题目：下列说法正确的是。
答案：一个程序可以包含多个源文件

2-47
题目：下列有关抽象类和接口的叙述中正确的是？
答案：含有抽象方法的类必须是抽象类，接口中的方法必须是抽象方法

2-48
题目：以对象为单位把某个对象写入文件,则需要使用什么方法?
答案：writeObject()

2-49
题目：若一个类对象能被整体写入文件，则定义该类时必须实现下列哪个接口?
答案：Serializable

2-50
题目：ServerSocket的getInetAddress()的返回值类型是
答案：InetAddress

2-51
题目：变量命名规范说法正确的是
答案：变量不能以数字作为开头

2-52
题目：哪一种类型的代码被JVM解释成本地代码？
答案：字节码

2-53
题目：下列程序中编译出错的行是？
答案：第5行

2-54
题目：以下描述错误的有
答案：abstract 可以修饰变量

2-55
题目：下列方法定义中，方法头不正确的是
答案：public static x(double b){return b;}

2-56
题目：关于java中的继承，下列说法错误的是
答案：java中的类采用的是多重继承

2-57
题目：使用流式套接字编程时，为了向对方发送数据，则需要使用哪个方法
答案：getOutputStream()

2-58
题目：创建一个网络服务器程序的正确执行顺序是？
答案：bdac

2-59
题目：在面向对象的软件系统中，不同类对象之间的通信的一种构造称为
答案：消息

2-60
题目：在Java中，实现了参数化类型的概念，使代码可以应用于多种类型的是？
答案：泛型
    """,
    "多选题": """3-1
题目：Java中有关线程的哪些叙述是正确的?
答案：使用start()方法可以使一个线程成为可运行的，但是它不一定立即开始运行；一个线程可能因为不同的原因停止并进入就绪状态。

3-2
题目：Java UDP编程主要用到的两个类是？
答案：DatagramSocket；DatagramPacket

3-3
题目：线程创建和启动--创建java.lang.Thread的子类MyThread实现多线程编程。利用MyThread类创建对象myThread。
答案：MyThread类必须重写父类的run()方法；myThread.start()方法用于启动线程，线程进入就绪状态，待该线程获得CPU，立即启动线程，线程一旦启动，执行该对象的run()方法。

3-4
题目：类的继承--在类的继承关系中，下列说法正确的是：
答案：子类属性与父类属性重名，子类对象调用该属性体现的是子类的属性值；子类方法覆盖父类方法，子类对象调用该方法时执行的是子类的方法体。

3-5
题目：子类对象创建--关于子类对象的创建过程及使用，下列说法正确的是：
答案：先执行父类的构造方法，再执行子类的构造方法；子类和父类中有重名的属性时，在子类对象里拥有它们各自的内存空间和属性值。

3-6
题目：访问权限--位于不同包但具有父子类关系，父类中哪些访问权限修饰的成员，在子类访问时不受限制?
答案：protected；public

3-7
题目：关于Java语言的特点，哪些是正确的？
答案：（未答对）

3-8
题目：在程序中利用throw或throws抛出异常，下列说法正确的是：
答案：（未答对）

3-9
题目：关于Java语言的描述，哪些是正确的?
答案：（未答对）

3-10
题目：文件读写--JAVA实现字符流写操作的类或接口包括下面的哪些?
答案：Writer；FileWriter

3-11
题目：文件读写--JAVA实现字符读取操作的类是：
答案：FileReader；BufferedReader；InputStreamReader；Reader

3-12
题目：HashMap特点--关于Java中的Map接口及其实现类HashMap，哪些说法是正确的？
答案：Map结构可以看成是键的集合、值的集合、键-值对的集合，因此遍历Map类型的对象，可以采取把三种集合展开的方式进行访问；Map结构中，键的集合是一个Set结构，里面的元素无序且不允许重复。

3-13
题目：Iterator方法--迭代器接口（Iterator）所定义的方法有：
答案：hasNext()；next()；remove()

3-14
题目：finally--关于Java异常的处理的finally语句块，哪些说法是正确的？
答案：（未答对）

3-15
题目：异常处理机制--关于Java中的异常的概念及处理机制，哪些说法是正确的？
答案：（未答对）

3-16
题目：interface--接口中定义常量（变量）时，默认含有哪些修饰符？
答案：public；static；final

3-17
题目：线程创建和启动--关于线程的创建和启动过程，下面说法正确的有哪些？
答案：定义Thread类的子类，重写Thread类的run()方法；创建该子类的实例对象，调用对象的start() 方法；定义一个实现Runnable接口的类，并实现run()方法；创建该类实例对象，将其作为参数传递给Thread类的构造方法来创建Thread对象，调用Thread对象的start() 方法。

3-18
题目：端口号--关于端口，下列说法中正确的是：
答案：（未答对）

3-19
题目：TCP协议--TCP协议是一种面向连接的、可靠的传输层协议。关于TCP协议通信过程哪些说法是正确的？
答案：（未答对）

3-20
题目：UDP通信--关于UDP协议通信的特点，下列说法正确的是：
答案：（未答对）

3-21
题目：下面说法正确的是：
答案：final 可修饰类、属性(变量)、方法；abstract可修饰类、方法；抽象方法只有方法头，没有方法体；关键字final和abstract不能同时使用。

3-22
题目：以下关于static关键字的说法正确的是：
答案：static关键字可以修饰成员变量；static关键字可以修饰代码块

3-23
题目：下列关于main方法的描述中，正确的是：
答案：在Java程序中，必须要有main方法；main方法可以保证Java程序独立运行；一个Java程序的主方法是main方法

3-24
题目：给出以下代码，请问Base类需要实现哪些构造方法？
答案：Base()；Base(int i)；Base(int j,int k)

3-25
题目：抽象类--关于Java中的抽象类，哪些说法是正确的？
答案：抽象类中可以含有抽象的方法，也可以含有非抽象的方法；含有抽象方法的类一定是抽象类；抽象类是不能用new操作来生成对象的，只能被子类继承；抽象类的子类如果实现了父类的所有抽象方法，它就是一个普通的类。如果没有实现抽象方法，则它还是抽象类。

3-26
题目：方法重写--子类重写父类方法时，哪些规则是正确的？
答案：方法名相同；参数相同；返回类型与父类定义相同或是父类返回类型的子类；访问权限≥父类被重写的方法定义的访问权限

3-27
题目：关于运行时异常，下列说法正确的是：
答案：（未答对）

3-28
题目：在java中，已定义了两个接口B和C，下面继承语句正确的是：
答案：interface A extends B,C；class A implements B,C""",
    "填空题": """
    4-1
题目：网络编程服务器端实现，补充代码：
Socket socket = s.accept();
BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
String str = in.readLine();
out.write(str);

4-2
题目：TCP客户端与服务器通信，补全代码：
Socket client = new Socket(IP, port);
class Server implements Runnable {
ServerSocket server = new ServerSocket(port);
Socket client = server.accept();
DataInputStream dis = new DataInputStream(client.getInputStream());

4-3
题目：使用BufferedReader按行读取键盘输入，BufferedWriter写入文件，补全代码：
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
BufferedWriter bw = new BufferedWriter(new FileWriter("D:/test.txt"));
String s = br.readLine();
bw.write(s);
bw.newLine();

4-4
题目：Java io包4个基本类：InputStream、OutputStream、Reader及Writer类。

4-5
题目：程序输出顺序：
第一行输出：1（This is a phone）
第二行输出：3（This is a mobilephone）
第三行输出：2（This is a Apple mobile phone）

4-6
题目：补全代码实现打印四个图形面积：
Shape[] ss = new Shape[4];
Circle构造函数：this.radius = radius;
getArea方法返回：(int)(3.14 * radius * radius + 0.5);

4-7
题目：程序运行输出结果：
输出：7ok

4-8
题目：程序运行输出结果：
输出：BDE

4-9
题目：程序输出结果：
输出：[-3, -2, -1] [-2, 0, 2]

4-10
题目：程序运行结果：
输出：0123443210

4-11
题目：Java中流按方向分为输入流和输出流。

4-12
题目：java.io包中处理字符数据的基本输入输出类是Reader和Writer。

4-13
题目：自定义异常类必须继承Exception类，人工抛出异常使用关键词throw。

4-14
题目：线程类中必须重写的方法是run()。

4-15
题目：启动线程使用的方法是start()。

4-16
题目：服务器端网络编程，补全代码：
Socket socket = s.accept();
BufferedReader in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
String str = in.readLine();
out.write(str);

4-17
题目：子类调用父类方法打印属性，代码：
super.printValue();

4-18
题目：Java中生成随机数的类：Math类和Random类。

4-19
题目：Iterator遍历集合时判断和取元素的方法是：hasNext() 和 next()。

4-20
题目：反射获取类对象的方法：
Class cla = p.getClass();
通过反射给属性赋值：nameField.set(p, "Jack");

4-21
题目：类实现接口必须实现全部方法，否则该类必须定义成抽象类。

4-22
题目：程序输出结果：
输出：z


    """,
    "程序填空题": """
    5-1
题目：Map操作。TreeMap的创建与遍历。
答案：

java
复制
编辑
TreeMap<String, Integer> treeMap = new TreeMap<>();//创建TreeMap,指定String、Integer泛型
Set<Map.Entry<String, Integer>> set = treeMap.entrySet();//获取treeMap的entry集（键值对集）
for (Entry<String, Integer> entry : set) { //for-each 语句实现entry集遍历
5-2
题目：【线程】线程同步。
答案：

java
复制
编辑
implements Runnable //定义售票线程
public synchronized void sell(){  //定义 同步方法
if(tickets > 0){      //判定票是否售完
5-3
题目：【集合】ArrayList列表遍历
答案：

java
复制
编辑
List<String> al=new ArrayList<>();//此处
while(listIter.hasNext())
System.out.println(listIter.next());
5-4
题目：【Java语言基础】输出Fibonacci数列
答案：

java
复制
编辑
f[i] = f[i-1] + f[i-2];
for(int i = 0;i<20;i++){
if((i+1) % 4 == 0)
5-5
题目：【线程，集合】计算整数序列和
答案：

java
复制
编辑
implements Runnable
sum=sum+(int) lt.get(i);//取出序列元素累加
ArrayList score= new ArrayList<>();//创建求和列表对象
SumList sl= new SumList(score);//创建 Runnable 接口实现类对象
th.start();//启动线程
5-6
题目：【异常】自定义异常类：成绩异常（ScoreException）
答案：

java
复制
编辑
extends Exception
throw new ScoreException();
else this.score = score;
try
System.out.println("程序结束");
5-7
题目：【类与对象】学生选课系统-类与对象
答案：

java
复制
编辑
return cNo;
public Course(String cNo, String cName, int credit){
this.credit = credit;
this.course = course;
stu[curNum++] = s;
this.course = course;
student[] s= new Student[NUM];//构造学生数组，数组长度是NUM
sCourse= new SelectCourse
for(int i=0;i< sCourse.getCurNum();i++){
5-8
题目：【网络编程】地址对象的应用
答案：

java
复制
编辑
InetAddress.getByName("www.cuit.edu.cn");
5-9 学校人事管理（共20分）
java
复制
编辑
class Person {
    public Person(
String name, int age, String gend
// 答案1 (2分)
er
) {
        this.name=name;
        this.age = age;
        this.gender=gender;
    }
    public String getName() {
        // 答案2 (2分)
return name;
    }
    public void setAge(int age) {
        // 答案3 (2分)
this.age = age;
    }
}
class Teacher 
extends Person
// 答案4 (2分)
{
    ...
}
class Student 
extends Person
// 答案5 (2分)
 {
    public void setScore(
// 答案6 (2分)
int[] score
) {
        this.score = score;
    }
    Student(String name, int age, String gender,int[] score,String grade){
        // 答案7 (2分)
super(name, age, gender);
        this.score=score;
        this.grade=grade;
    }
}
public class Main {
    public static void main(
// 答案8 (2分)
String[] args
) {
        ...
        for(int i=0;i<5;i++)
            stu[i]=
// 答案9 (2分)
new Student();
        ...
        stu[1].setScore(
// 答案10 (2分)
new int[]{115, 125, 138, 105, 120}
);
        ...
    }
}
5-10 学生选课系统（共24分）
java
复制
编辑
class Course {
    public Course(
// 答案1 (2分)
String cNo, String cName, int credit
){
    this.cNo=cNo;
    this.cName=cName;
    this.credit=credit;        
}
public void setCNo(String no) {
// 答案2 (2分)
this.cNo = no;
}
public void setCredit(
// 答案3 (2分)
int credit
) {
    this.credit = credit;
}
}
class student {
    public student(
// 答案4 (2分)
String no, String name, String subject
){
    this.no=no;
    this.name=name;
    this.subject=subject;        
}
}
class SelectCourse {
    public SelectCourse(
// 答案5 (2分)
Course course, student[] stu, int maxNum, int curNum
){
    this.course=course;
    this.stu =stu;
    this.maxNum=maxNum;
    this.curNum=curNum;
}
public void appendStu(student s){
    if(curNum<maxNum){
        // 答案6 (2分)
        stu[curNum++] = s;
    }
}
public void setCourse(Course course) {
// 答案7 (2分)
this.course = course;
}
}
public class Main {
    public static void main(
// 答案8 (2分)
String[] args
) {
    ...
    student[] s=
// 答案9 (2分)
new student[NUM];
    ...
    sCourse=
// 答案10 (2分)
new SelectCourse(course,s,100,3);
    ...
    for(int i=0;i<
// 答案11 (2分)
sCourse.getCurNum()
;i++){
        ...
    }
}
}
5-11 House类实现Comparable及异常处理（共15分）
java
复制
编辑
import java.util.Scanner;
// 答案1 (1分)
import java.util.Scanner;

class House implements  
// 答案2 (1分)
Comparable<House>
{
    public House(
// 答案3 (1分)
String address, double area, double price
){
    setAddress(address);
    setArea(area);
    // 答案4 (1分)
    setPrice(price);
}
public String getAddress() {
// 答案5 (1分)
return address;
}
public void setAddress(String address) {
// 答案6 (1分)
this.address = address;
}
public void setArea(double area) {
    if(area>0)
      this.area = area;
    else
        throw 
// 答案7 (1分)
new IllegalArgumentException("住宅的面积必须大于0");
}
public void setPrice(double price) {
    if(
// 答案8 (1分)
price > 0
)
      this.price = price;
    else
      throw 
// 答案9 (1分)
new IllegalArgumentException("住宅的价格必须大于0");
}
public int compareTo(House o) {
    if (price/area > o.price/o.area)
       return 1;
    else if (
// 答案10 (1分)
price/area < o.price/o.area
)
       return -1;
    else
// 答案11 (1分)
return 0;
}
}
public class Main {
    public static void main(String[] args) {
        Scanner input = new Scanner(
// 答案12 (1分)
System.in
);
        for(int i=0; i<10; i++) {
            try
// 答案13 (1分)
{
                House house1 = new House(input.next(), input.nextDouble(), input.nextDouble());
                House house2 = new House(input.next(), input.nextDouble(), input.nextDouble());
                House maxHouse;
                if (house1.
// 答案14 (1分)
compareTo(house2)
 >= 0)
                    maxHouse = house1;
                else
// 答案15 (1分)
maxHouse = house2;
                System.out.println("The max of " + house1 + " and " + house2 + " is " + maxHouse);
            } catch (IllegalArgumentException e1) {
                System.out.println(e1.getMessage());
                input.nextLine();
            } catch (Exception e2) {
                System.out.println(e2.getMessage());
                input.nextLine();
            }
        }
    }
}
5-12 线程同步计数（共6分）
java
复制
编辑
class BackCounter implements Runnable{
    public void  run() {
        for(int i=10;i>0;i--) {
            // 答案1 (2分)
            synchronized(this) {
                if( count<=0 ) break;
                count--;
            }
            ...
        }
    }
}
public class Main {
    public static void main(String[] args) throws InterruptedException {
        ...
        for (Thread th:lt)
            // 答案2 (2分)
            th.start();
        for (Thread th:lt)
            // 答案3 (2分)
            th.join();
        System.out.println(bc.getCount());
    }
}
5-13 判断闰年（共5分）
java
复制
编辑
import java.util.Scanner;
// 答案1 (1分)
import java.util.Scanner;

public class Main{
    public static void main(String[] args) {
        int year;
        Scanner sc = new Scanner(System.in);
        for(int i=0;i<2;i++){
            // 答案2 (1分)
            year = sc.nextInt();
            if(
// 答案3 (1分)
(year % 4 == 0 && year % 100 != 0) || year % 400 == 0
) {
                // 答案4 (1分)
                System.out.println("Yes");
            }
            else {
                // 答案5 (1分)
                System.out.println("No");
            }
        }
    }
}
5-14 集合排序查找（共5分）
java
复制
编辑
class Student implements Comparable  {
    public Student(String name, int age) {
        // 答案1 (1分)
        this.name = name;
        this.age = age;
    }
    public int compareTo(Student stu) {
        // 答案2 (1分)
        return this.age - stu.age;
    }
}
public class Main {
    public static void main(String args[ ]) {
        List  list = new LinkedList();
        Scanner sc = new Scanner(System.in);
        list.add(new Student(sc.next(), sc.nextInt()));
        list.add(new Student(sc.next(), sc.nextInt()));
        list.add(new Student(sc.next(), sc.nextInt()));
        Iterator   it = 
        // 答案3 (1分)
        list.iterator();
        Collections.
// 答案4 (1分)
sort(list);
        for(int i=0;i<2;i++){
            Student stu4 = new Student(sc.next(), sc.nextInt());
            int index = Collections.binarySearch(list, stu4);
            if (
// 答案5 (1分)
index >= 0
)
               System.out.println("【"+stu4.name+"】" + "与链表中的" + "【"+list.get(index).name+"】" + "年龄相同");
            else
                System.out.println("链表中的对象，没有一个与" + "【"+stu4.name+"】"  + "年龄相同的");
        }
    }
}
5-15 读入两个整数求和（共9分）
java
复制
编辑
public class Main {
    public static void main (String args[]) {
          Scanner reader = new Scanner(System.in);
          int a= 
          // 答案1 (3分)
          reader.nextInt();
          int b= 
          // 答案2 (3分)
          reader.nextInt();
          System.out.print(
          // 答案3 (3分)
          a + b
          );  
    }
}
5-16 Map操作（共6分）
java
复制
编辑
public class Main {
    public static void main(String args[]) {
        HashMap<String, Integer> hashMap = new HashMap<String, Integer>();
        hashMap.put("Tom", new Integer(23));
        Set<Map.Entry<String, Integer>> set = 
        // 答案1 (2分)
        hashMap.entrySet();
        for (
        // 答案2 (2分)
        Map.Entry<String, Integer> entry : set
        ) {
            System.out.println(entry.getKey() + "-" + entry.getValue());
        }
        Set<String> keySet = 
        // 答案3 (2分)
        hashMap.keySet();
        ...
    }
}
5-17 Set的操作
题干（保留）：构造泛型为String的TreeSet对象，添加元素，并遍历输出。
答案填空：

java
复制
编辑
TreeSet<String> treeSet = new TreeSet<String>();
for (String str : treeSet) {
5-18 线程同步，售票系统
题干（保留）：4个窗口售票，不允许重票、错票，要求同步方法。
答案填空：

java
复制
编辑
public synchronized void sell() {
    if (tickets > 0) {
5-19 简单的学生选课系统
题干（保留）：设计课程类、学生类、选课类，完成构造函数及方法填空。
答案填空：

Course类

java
复制
编辑
return cNo;
java
复制
编辑
public Course(String cNo, String cName, int credit) {
java
复制
编辑
this.cNo = no;
student类

java
复制
编辑
public student(String no, String name, String subject) {
java
复制
编辑
this.no = no;
this.name = name;
this.subject = subject;
SelectCourse类

java
复制
编辑
public SelectCourse(Course course, student[] stu, int maxNum, int curNum) {
java
复制
编辑
stu[curNum++] = s;
java
复制
编辑
this.course = course;
java
复制
编辑
student[] s = new student[NUM];
java
复制
编辑
sCourse = new SelectCourse(course, s, 100, 3);
java
复制
编辑
for (int i = 0; i < sCourse.getCurNum(); i++) {
5-20 利用线程进行计算整数序列和
题干（保留）：输入多组序列，计算每组整数和，使用线程。
答案填空：

java
复制
编辑
ArrayList<Integer> score = new ArrayList<>();
java
复制
编辑
SumList sl = new SumList(score);
java
复制
编辑
Thread th = new Thread(sl);
java
复制
编辑
class SumList implements Runnable {
5-21 【类与对象】方法重载，实现2个和3个整数的相加
题干（保留）：使用方法重载，实现加法。
答案填空：

java
复制
编辑
public int add(int a, int b) {
java
复制
编辑
AddOver a = new AddOver();
5-22 【集合】创建ArrayList并采用Iterator、下标索引、foreach遍历
题干（保留）：初始化ArrayList，遍历输出。
答案填空：

java
复制
编辑
arrayList = new ArrayList<>();
java
复制
编辑
Iterator<String> iterator = arrayList.iterator();
java
复制
编辑
while (iterator.hasNext())
java
复制
编辑
arrayList.get(i)
java
复制
编辑
for (String ar : arrayList)
    """,
    "继承与多态】从抽象类shape类扩展出一个长方形类Rectangle": """
    class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * (width + height);
    }
}""",
    "6-2 本科生的成绩等级计算。假设某班级里既有本科生也有研究生 , 请编写程序统计出全班学生的成绩等级并显示出来。": """
        public String scoreLevel(double score) {
        if (score >= 80) return "优秀";
        else if (score >= 70) return "良好";
        else if (score >= 60) return "一般";
        else if (score >= 50) return "及格";
        else return "不及格";
    }

    """,
    "6-3 写一个函数,从键盘接收一个整数n,输出1+2+3+...+n的和": """
    public static int add(int n) {
    return n * (n + 1) / 2;
}
    """,
    "6-4 线程实现倒计时": """
    import java.util.Scanner;
class CountDown implements Runnable {
    @Override
    public void run() {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        if (n < 0) {
            System.out.println("输入数据有误");
            return;
        }
        
        for (int i = n; i >= 0; i--) {
            System.out.println(i);
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
    """,
    "6-5 ArrayList并采用Iterator迭代器、下标索引、foreach进行遍历": """
    public static void travel(String a, String b, String c, String d) {
    ArrayList<String> list = new ArrayList<>();
    list.add(a);
    list.add(b);
    list.add(c);
    list.add(d);
    
    Iterator<String> it = list.iterator();
    while (it.hasNext()) {
        System.out.println(it.next());
    }
    
    for (int i = 0; i < list.size(); i++) {
        System.out.println(list.get(i));
    }
    
    for (String s : list) {
        System.out.println(s);
    }
}
    """,
    "6-6 从抽象类shape类扩展出一个圆形类Circle": """
    class Circle extends Shape {
    private double r;
    
    public Circle(double r) {
        this.r = r;
    }
    
    @Override
    public double getArea() {
        return Math.PI * r * r;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * Math.PI * r;
    }
}
    """,
    "6-7 判断今年盈利是否达到公司标准": """
    class Subsidiary extends Company {
    @Override
    public void applyRule(double income, double pay) {
        double total = income - pay;
        if (total >= 200) {
            System.out.println("分公司总成绩为 : " + total + "万,达到了要求");
        } else {
            System.out.println("分公司总成绩为 : " + total + "万,未达到要求");
        }
    }
}
    """,
    "6-8 多线程输出递增数字": """class PrintRunnable implements Runnable {
    private final int threadId;
    private static int currentNum = 1;
    private static final Object lock = new Object();
    private static int activeThread = 1;

    public PrintRunnable(int threadId, Object o) {
        this.threadId = threadId;
    }

    @Override
    public void run() {
        while (currentNum <= 15) {
            synchronized (lock) {
                while (threadId != activeThread) {
                    try {
                        lock.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                    if (currentNum > 15) return;
                }

                for (int i = 0; i < 5 && currentNum <= 15; i++) {
                    System.out.println("线程" + threadId + ":" + currentNum++);
                }

                activeThread = activeThread % 3 + 1;
                lock.notifyAll();
            }
        }
    }
}""",
    "6-9 给定一种规律 pattern 和一个字符串 str ，判断 str 是否遵循相同的规律": """public static boolean wordPattern(String pattern, String str) {
    String[] words = str.split(" ");
    if (pattern.length() != words.length) return false;
    
    HashMap<Character, String> charToWord = new HashMap<>();
    HashMap<String, Character> wordToChar = new HashMap<>();
    
    for (int i = 0; i < pattern.length(); i++) {
        char c = pattern.charAt(i);
        String word = words[i];
        
        if (charToWord.containsKey(c)) {
            if (!charToWord.get(c).equals(word)) return false;
        } else {
            if (wordToChar.containsKey(word)) return false;
            charToWord.put(c, word);
            wordToChar.put(word, c);
        }
    }
    return true;
}""",
    "2.编写一个应用程序求三个整数的平均数，这里三个数字通过键盘输入获取（原始数字要求从命令行输入，应用程序中main方法的参数String类型的数组args能接受用户从命令行键入的参数）。": """
    import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // 提示用户输入三个整数
       System.out.println("请输入三个整数：");
        int num1 = scanner.nextInt();

        //System.out.print("请输入第二个整数: ");
        int num2 = scanner.nextInt();

        //System.out.print("请输入第三个整数: ");
        int num3 = scanner.nextInt();

        // 计算平均值
        double average = (num1 + num2 + num3) / 3.0;

        // 输出平均值
        System.out.println("平均数为：" + average);

        scanner.close();
    }
}""",
    "建立三个线程，并且同时运行它们。当运行时输出线程的名称。": """
    public class Main {
    public static void main(String[] args) {
       
        Thread thread1 = new Thread(new MyRunnable(), "thread 1");
        Thread thread2 = new Thread(new MyRunnable(), "thread 2");
        Thread thread3 = new Thread(new MyRunnable(), "thread 3");
        
        thread1.start();
        thread2.start();
        thread3.start();
    }
}

class MyRunnable implements Runnable {
    @Override
    public void run() {
        
        for (int i = 0; i < 5; i++) {
            System.out.println("the thread is: " + Thread.currentThread().getName());
            try {
            
                Thread.sleep((long)(Math.random() * 100));
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
    """,
    "实现3个类：Storage、Counter和Printer。 Storage类应存储整数。 Counter应创建线程，线程从0开始计数（0,1,2,3…）并将每个值存储到Storage类中。 Printer类应创建一个线程，线程读取Storage类中的值并打印值。编写程序创建Storage类的实例，并创建一个Counter对象和Printer对象操作此实例。": """
    package com.yxx.Deom7;


class Storage {
    private int value;
    private boolean available = false;

    public synchronized void setValue(int value) {
        while (available) {
            try {
                wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        this.value = value;
        available = true;
        notifyAll();
    }

    public synchronized int getValue() {
        while (!available) {
            try {
                wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        available = false;
        notifyAll();
        return value;
    }
}

class Counter implements Runnable {
    private Storage storage;

    public Counter(Storage storage) {
        this.storage = storage;
    }

    @Override
    public void run() {
        for (int i = 0; ; i++) {
            storage.setValue(i);
            System.out.println("Counter写入" + i);
           
        }
    }
}

class Printer implements Runnable {
    private Storage storage;

    public Printer(Storage storage) {
        this.storage = storage;
    }

    @Override
    public void run() {
        while (true) {
            int value = storage.getValue();
            System.out.println("Printer输出" + value);
           
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Storage storage = new Storage();
        Counter counter = new Counter(storage);
        Printer printer = new Printer(storage);

        new Thread(counter).start();
        new Thread(printer).start();
    }
}""",
    " 修改第2题的程序，添加适当代码，以确保每个数字都恰好只被打印一次。": """package com.yxx.Deom7;


class Storage {
    private int value;
    private boolean available = false;

    public synchronized void setValue(int value) {
        while (available) {
            try {
                wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        this.value = value;
        available = true;
        notifyAll();
    }

    public synchronized int getValue() {
        while (!available) {
            try {
                wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        available = false;
        notifyAll();
        return value;
    }
}

class Counter implements Runnable {
    private Storage storage;

    public Counter(Storage storage) {
        this.storage = storage;
    }

    @Override
    public void run() {
        for (int i = 0; ; i++) {
            storage.setValue(i);
            System.out.println("Counter写入" + i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class Printer implements Runnable {
    private Storage storage;

    public Printer(Storage storage) {
        this.storage = storage;
    }

    @Override
    public void run() {
        while (true) {
            int value = storage.getValue();
            System.out.println("Printer输出" + value);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

public class Main {
    public static void main(String[] args) {
        Storage storage = new Storage();
        Counter counter = new Counter(storage);
        Printer printer = new Printer(storage);

        new Thread(counter).start();
        new Thread(printer).start();
    }
}""",
    "1.编写一个圆环类 Ring 的 Java 程序。圆环类有 3 个数据成员 , 分别是内半径 innerRadius, 外半径 outerRadius 和颜色 color, 这些属性可以查看 get 也可以重新设置 set, 另外 , 圆环还可以返回其面积 area 。 ": """
    import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double innerRadius = scanner.nextDouble();
        double outerRadius = scanner.nextDouble();
        
        Ring ring = new Ring(innerRadius, outerRadius, "red");
        System.out.println("圆环的面积为" + ring.area());
    }
}

class Ring {
    private double innerRadius;
    private double outerRadius;
    private String color;

    public Ring(double innerRadius, double outerRadius, String color) {
        this.innerRadius = innerRadius;
        this.outerRadius = outerRadius;
        this.color = color;
    }

    public double area() {
        return Math.PI * (outerRadius * outerRadius - innerRadius * innerRadius);
    }

    // Getter and Setter methods
    public double getInnerRadius() { return innerRadius; }
    public void setInnerRadius(double innerRadius) { this.innerRadius = innerRadius; }
    
    public double getOuterRadius() { return outerRadius; }
    public void setOuterRadius(double outerRadius) { this.outerRadius = outerRadius; }
    
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}""",
    "2.第3-1题中增加两个static 成员 ：圆周率和圆对象个数, 增加两个 static 方法，分别是设置圆周率(3.14)和显示当前圆对象个数的, 仔细体会静态成员与实例成员的使用方法和区别。 两个圆半径分别为3和2。": """
    public class Main {
    public static void main(String[] args) {
        Ring.setPi(3.14);
        Ring ring1 = new Ring(2, 3, "red");
        Ring ring2 = new Ring(1, 4, "blue");
        
        System.out.printf("圆环面积：%.2f\n", ring1.area());
        System.out.println("PI:" + Ring.getPi());
        System.out.println("对象个数:" + Ring.getCount());
    }
}

class Ring {
    private double innerRadius;
    private double outerRadius;
    private String color;
    private static double pi = Math.PI;
    private static int count = 0;

    public Ring(double innerRadius, double outerRadius, String color) {
        this.innerRadius = innerRadius;
        this.outerRadius = outerRadius;
        this.color = color;
        count++;
    }

    public double area() {
        return pi * (outerRadius * outerRadius - innerRadius * innerRadius);
    }

    public static void setPi(double pi) { Ring.pi = pi; }
    public static double getPi() { return pi; }
    public static int getCount() { return count; }


    public double getInnerRadius() { return innerRadius; }
    public void setInnerRadius(double innerRadius) { this.innerRadius = innerRadius; }
    
    public double getOuterRadius() { return outerRadius; }
    public void setOuterRadius(double outerRadius) { this.outerRadius = outerRadius; }
    
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
}""",
    "设计一个教材类，一个课程类，及一个为某门课程指定参考教材的类。一门课程可以有多本参考教材，再设计一个测试类。": """
    import java.util.ArrayList;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.println("请输入课程名称：");
        String courseName = scanner.nextLine();
        
        System.out.println("请输入教材数量：");
        int bookCount = scanner.nextInt();
        scanner.nextLine();  // 消耗换行符
        
        Course course = new Course(courseName);
        
        for (int i = 0; i < bookCount; i++) {
            System.out.println("请输入第" + (i + 1) + "本书名");
            String bookName = scanner.nextLine();
            course.addBook(new Book(bookName));
        }
        
        System.out.println("\n你的课程是：" + course.getName());
        ArrayList<Book> books = course.getBooks();
        for (int i = 0; i < books.size(); i++) {
            System.out.println("第" + (i + 1) + "本书名为" + books.get(i).getName());
        }
    }
}

class Book {
    private String name;
    
    public Book(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
}

class Course {
    private String name;
    private ArrayList<Book> books;
    
    public Course(String name) {
        this.name = name;
        this.books = new ArrayList<>();
    }
    
    public void addBook(Book book) {
        books.add(book);
    }
    
    public String getName() {
        return name;
    }
    
    public ArrayList<Book> getBooks() {
        return books;
    }
}""",
    "设计一个简单的学校人事管理系统,管理教师和学生信息。实现教师与学生基本信息的添加、删除、修改、查询。其中编号、姓名、性别、出生日期为共有的，教师包括部门、职称、工资；学生包括高考分数、专业field、班级等。": """
    package com.yxx.Deom7;


import java.util.*;
import java.text.SimpleDateFormat;

public class SchoolManagementSystem {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        ManagementSystem system = new ManagementSystem();

        while (true) {
            System.out.println("\n===== 学校人事管理系统 =====");
            System.out.println("1. 添加教师");
            System.out.println("2. 添加学生");
            System.out.println("3. 删除人员");
            System.out.println("4. 修改人员");
            System.out.println("5. 查询人员");
            System.out.println("6. 显示所有人员");
            System.out.println("0. 退出系统");
            System.out.print("请选择操作: ");

            int choice = scanner.nextInt();
            scanner.nextLine(); 

            switch (choice) {
                case 1:
                    addTeacher(scanner, system);
                    break;
                case 2:
                    addStudent(scanner, system);
                    break;
                case 3:
                    deletePerson(scanner, system);
                    break;
                case 4:
                    updatePerson(scanner, system);
                    break;
                case 5:
                    searchPerson(scanner, system);
                    break;
                case 6:
                    system.displayAll();
                    break;
                case 0:
                    System.out.println("感谢使用，再见！");
                    return;
                default:
                    System.out.println("无效选择，请重新输入！");
            }
        }
    }

    private static void addTeacher(Scanner scanner, ManagementSystem system) {
        System.out.println("\n--- 添加教师 ---");
        System.out.print("请输入编号: ");
        String id = scanner.nextLine();

        System.out.print("请输入姓名: ");
        String name = scanner.nextLine();

        System.out.print("请输入性别: ");
        String gender = scanner.nextLine();

        System.out.print("请输入出生日期(格式: yyyy-MM-dd): ");
        String birthDate = scanner.nextLine();

        System.out.print("请输入部门: ");
        String department = scanner.nextLine();

        System.out.print("请输入职称: ");
        String title = scanner.nextLine();

        System.out.print("请输入工资: ");
        double salary = scanner.nextDouble();
        scanner.nextLine(); 

        Teacher teacher = new Teacher(id, name, gender, birthDate, department, title, salary);
        system.addPerson(teacher);
        System.out.println("教师添加成功！");
    }

    private static void addStudent(Scanner scanner, ManagementSystem system) {
        System.out.println("\n--- 添加学生 ---");
        System.out.print("请输入编号: ");
        String id = scanner.nextLine();

        System.out.print("请输入姓名: ");
        String name = scanner.nextLine();

        System.out.print("请输入性别: ");
        String gender = scanner.nextLine();

        System.out.print("请输入出生日期(格式: yyyy-MM-dd): ");
        String birthDate = scanner.nextLine();

        System.out.print("请输入高考分数: ");
        double gaokaoScore = scanner.nextDouble();
        scanner.nextLine(); // 消耗换行符

        System.out.print("请输入专业: ");
        String major = scanner.nextLine();

        System.out.print("请输入班级: ");
        String className = scanner.nextLine();

        Student student = new Student(id, name, gender, birthDate, gaokaoScore, major, className);
        system.addPerson(student);
        System.out.println("学生添加成功！");
    }

    private static void deletePerson(Scanner scanner, ManagementSystem system) {
        System.out.print("\n请输入要删除的人员编号: ");
        String id = scanner.nextLine();
        system.deletePerson(id);
    }

    private static void updatePerson(Scanner scanner, ManagementSystem system) {
        System.out.print("\n请输入要修改的人员编号: ");
        String id = scanner.nextLine();

        System.out.println("请选择要修改的信息:");
        System.out.println("1. 姓名");
        System.out.println("2. 性别");
        System.out.println("3. 出生日期");

        if (system.isTeacher(id)) {
            System.out.println("4. 部门");
            System.out.println("5. 职称");
            System.out.println("6. 工资");
        } else if (system.isStudent(id)) {
            System.out.println("4. 高考分数");
            System.out.println("5. 专业");
            System.out.println("6. 班级");
        } else {
            System.out.println("未找到该人员！");
            return;
        }

        System.out.print("请选择: ");
        int field = scanner.nextInt();
        scanner.nextLine(); // 消耗换行符

        System.out.print("请输入新值: ");
        String value = scanner.nextLine();

        system.updatePerson(id, field, value);
    }

    private static void searchPerson(Scanner scanner, ManagementSystem system) {
        System.out.println("\n--- 查询人员 ---");
        System.out.println("1. 按编号查询");
        System.out.println("2. 按姓名查询");
        System.out.print("请选择查询方式: ");
        int type = scanner.nextInt();
        scanner.nextLine(); 

        if (type == 1) {
            System.out.print("请输入人员编号: ");
            String id = scanner.nextLine();
            system.searchById(id);
        } else if (type == 2) {
            System.out.print("请输入人员姓名: ");
            String name = scanner.nextLine();
            system.searchByName(name);
        } else {
            System.out.println("无效选择！");
        }
    }
}

class ManagementSystem {
    private final Map<String, Person> persons = new HashMap<>();
    private final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");

    public void addPerson(Person person) {
        persons.put(person.getId(), person);
    }

    public void deletePerson(String id) {
        if (persons.containsKey(id)) {
            persons.remove(id);
            System.out.println("人员删除成功！");
        } else {
            System.out.println("未找到该人员！");
        }
    }

    public void updatePerson(String id, int field, String value) {
        Person person = persons.get(id);
        if (person == null) {
            System.out.println("未找到该人员！");
            return;
        }

        try {
            switch (field) {
                case 1: 
                    person.setName(value);
                    break;
                case 2: 
                    person.setGender(value);
                    break;
                case 3:
                    dateFormat.parse(value); // 验证日期格式
                    person.setBirthDate(value);
                    break;
                case 4:
                    if (person instanceof Teacher) {
                        ((Teacher) person).setDepartment(value);
                    } else if (person instanceof Student) {
                        ((Student) person).setGaokaoScore(Double.parseDouble(value));
                    }
                    break;
                case 5: 
                    if (person instanceof Teacher) {
                        ((Teacher) person).setTitle(value);
                    } else if (person instanceof Student) {
                        ((Student) person).setMajor(value);
                    }
                    break;
                case 6: 
                    if (person instanceof Teacher) {
                        ((Teacher) person).setSalary(Double.parseDouble(value));
                    } else if (person instanceof Student) {
                        ((Student) person).setClassName(value);
                    }
                    break;
                default:
                    System.out.println("无效的字段选择！");
                    return;
            }
            System.out.println("信息更新成功！");
        } catch (Exception e) {
            System.out.println("更新失败: " + e.getMessage());
        }
    }

    public void searchById(String id) {
        Person person = persons.get(id);
        if (person != null) {
            person.display();
        } else {
            System.out.println("未找到该人员！");
        }
    }

    public void searchByName(String name) {
        boolean found = false;
        for (Person person : persons.values()) {
            if (person.getName().equalsIgnoreCase(name)) {
                person.display();
                found = true;
            }
        }
        if (!found) {
            System.out.println("未找到该人员！");
        }
    }

    public void displayAll() {
        if (persons.isEmpty()) {
            System.out.println("系统中暂无人员信息！");
            return;
        }

        System.out.println("\n===== 所有人员信息 =====");
        for (Person person : persons.values()) {
            person.display();
            System.out.println("----------------------");
        }
    }

    public boolean isTeacher(String id) {
        return persons.get(id) instanceof Teacher;
    }

    public boolean isStudent(String id) {
        return persons.get(id) instanceof Student;
    }
}

abstract class Person {
    private String id;
    private String name;
    private String gender;
    private String birthDate;

    public Person(String id, String name, String gender, String birthDate) {
        this.id = id;
        this.name = name;
        this.gender = gender;
        this.birthDate = birthDate;
    }

    public abstract void display();

    // Getters and Setters
    public String getId() { return id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    public String getBirthDate() { return birthDate; }
    public void setBirthDate(String birthDate) { this.birthDate = birthDate; }
}

class Teacher extends Person {
    private String department;
    private String title;
    private double salary;

    public Teacher(String id, String name, String gender, String birthDate,
                   String department, String title, double salary) {
        super(id, name, gender, birthDate);
        this.department = department;
        this.title = title;
        this.salary = salary;
    }

    @Override
    public void display() {
        System.out.println("教师信息:");
        System.out.println("编号: " + getId());
        System.out.println("姓名: " + getName());
        System.out.println("性别: " + getGender());
        System.out.println("出生日期: " + getBirthDate());
        System.out.println("部门: " + department);
        System.out.println("职称: " + title);
        System.out.printf("工资: %.2f\n", salary);
    }

 
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public double getSalary() { return salary; }
    public void setSalary(double salary) { this.salary = salary; }
}

class Student extends Person {
    private double gaokaoScore;
    private String major;
    private String className;

    public Student(String id, String name, String gender, String birthDate,
                   double gaokaoScore, String major, String className) {
        super(id, name, gender, birthDate);
        this.gaokaoScore = gaokaoScore;
        this.major = major;
        this.className = className;
    }

    @Override
    public void display() {
        System.out.println("学生信息:");
        System.out.println("编号: " + getId());
        System.out.println("姓名: " + getName());
        System.out.println("性别: " + getGender());
        System.out.println("出生日期: " + getBirthDate());
        System.out.println("高考分数: " + gaokaoScore);
        System.out.println("专业: " + major);
        System.out.println("班级: " + className);
    }

    // Getters and Setters
    public double getGaokaoScore() { return gaokaoScore; }
    public void setGaokaoScore(double gaokaoScore) { this.gaokaoScore = gaokaoScore; }
    public String getMajor() { return major; }
    public void setMajor(String major) { this.major = major; }
    public String getClassName() { return className; }
    public void setClassName(String className) { this.className = className; }
}""",
    "设计 3 个类 , 分别是学生类 Student, 本科生类 Undergaduate, 研究生类 Postgraduate, 其中 Student 类是一个抽象类 , 它包含一些基本的学生信息如姓名、所学课程、课程成绩等 , 而 Undergraduate 类和 Postgraduate 都是 Student 类的子类 , 它们之间的主要差别是计算课程成绩等级的方法有所不同 , 研究生的标准要比本科生的标准高一些 , 如下表所示。": """
    package com.yxx.Deom7;

import java.util.ArrayList;


public class StudentManagementSystem {
    public static void main(String[] args) {

        ArrayList<StudentM> students = new ArrayList<>();


        students.add(new Undergraduate("张三", 85));
        students.add(new Undergraduate("李四", 75));
        students.add(new Undergraduate("王五", 55));
        students.add(new Undergraduate("赵六", 45));


        students.add(new Postgraduate("钱七", 95));
        students.add(new Postgraduate("孙八", 85));
        students.add(new Postgraduate("周九", 75));
        students.add(new Postgraduate("吴十", 65));
        students.add(new Postgraduate("郑十一", 55));


        System.out.println("全班学生成绩等级统计:");
        System.out.println("====================================");

        for (StudentM student : students) {
            System.out.printf("%-8s (%s): %d分 -> %s%n",
                    student.getName(),
                    student.getStudentType(),
                    student.getScore(),
                    student.getGrade());
        }
    }
}


abstract class StudentM {
    private String name;
    private int score;

    public StudentM(String name, int score) {
        this.name = name;
        this.score = score;
    }

    public String getName() {
        return name;
    }

    public int getScore() {
        return score;
    }


    public abstract String getGrade();


    public abstract String getStudentType();
}


class Undergraduate extends StudentM {
    public Undergraduate(String name, int score) {
        super(name, score);
    }

    @Override
    public String getGrade() {
        int score = getScore();
        if (score >= 80) return "优秀";
        else if (score >= 70) return "良好";
        else if (score >= 60) return "一般";
        else if (score >= 50) return "及格";
        else return "不及格";
    }

    @Override
    public String getStudentType() {
        return "本科生";
    }
}


class Postgraduate extends StudentM {
    public Postgraduate(String name, int score) {
        super(name, score);
    }

    @Override
    public String getGrade() {
        int score = getScore();
        if (score >= 90) return "优秀";
        else if (score >= 80) return "良好";
        else if (score >= 70) return "一般";
        else if (score >= 60) return "及格";
        else return "不及格";
    }

    @Override
    public String getStudentType() {
        return "研究生";
    }
}""",
    " 编写文本文件复制程序，即把源文件复制到目标文件，运行时用参数方式输入源文件名和目标文件名，设入口主类为FileCopy，则运行方式为：": """
    package com.yxx.Deom7;

import java.io.*;

public class FileCopy {
    public static void main(String[] args) {

        if (args.length != 2) {
            System.err.println("method: java FileCopy <Based File> <Gouat File>");
            System.exit(1);
        }

        String sourceFile = args[0];
        String destFile = args[1];

        try (
                InputStream in = new FileInputStream(sourceFile);
                OutputStream out = new FileOutputStream(destFile)
        ) {
            byte[] buffer = new byte[8192];
            int bytesRead;


            while ((bytesRead = in.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
            }

            System.out.println("Succeced: " + sourceFile + " -> " + destFile);

        } catch (FileNotFoundException e) {
            System.err.println("error - " + e.getMessage());
        } catch (IOException e) {
            System.err.println("IOError " + e.getMessage());
        }
    }
}""",
    "将任意两个文件合并到一个文件，要求采用java命令行方式在控制台按照“源文件1 源文件2 目标文件” 方式录入，注意多种异常处理。": """
    package com.yxx.Deom7;

import java.io.*;

public class FileMerge {
    public static void main(String[] args) {
        if (args.length != 3) {
            System.err.println("用法: java FileMerge <源文件1> <源文件2> <目标文件>");
            System.exit(1);
        }

        String sourceFile1 = args[0];
        String sourceFile2 = args[1];
        String destFile = args[2];

        try {

            createParentDirs(destFile);

            mergeFiles(sourceFile1, sourceFile2, destFile);

            System.out.println("文件合并成功: " + sourceFile1 + " + " + sourceFile2 + " → " + destFile);

        } catch (FileNotFoundException e) {
            System.err.println("错误: 源文件不存在 - " + e.getMessage());
        } catch (IOException e) {
            System.err.println("错误: " + e.getMessage());
        }
    }

    private static void createParentDirs(String filePath) throws IOException {
        File file = new File(filePath);
        File parentDir = file.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            parentDir.mkdirs();
        }
    }

    private static void mergeFiles(String source1, String source2, String dest) throws IOException {
        try (InputStream in1 = new FileInputStream(source1);
             InputStream in2 = new FileInputStream(source2);
             OutputStream out = new FileOutputStream(dest)) {

            copyStream(in1, out);

            copyStream(in2, out);
        }
    }

    private static void copyStream(InputStream in, OutputStream out) throws IOException {
        byte[] buffer = new byte[8192];
        int bytesRead;
        while ((bytesRead = in.read(buffer)) != -1) {
            out.write(buffer, 0, bytesRead);
        }
    }
}""",
    "编写程序实现将一个文件内容追加到另一个文件内容后，如将D盘file文件夹下的f1.txt追加到E盘根目录下的f2.txt中。(必须异常处理)": """
    package com.yxx.Deom7;

import java.io.*;
import java.nio.file.*;

public class FileAppend {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.err.println("用法: java FileAppend <源文件> <目标文件>");
            System.exit(1);
        }

        String sourceFile = args[0];
        String destFile = args[1];

        try {
           
            createParentDirs(destFile);

            appendFile(sourceFile, destFile);

            System.out.println("文件追加成功: " + sourceFile + " → " + destFile);

        } catch (FileNotFoundException e) {
            System.err.println("错误: 源文件不存在 - " + e.getMessage());
        } catch (IOException e) {
            System.err.println("错误: " + e.getMessage());
        }
    }

    private static void createParentDirs(String filePath) throws IOException {
        Path path = Paths.get(filePath);
        if (path.getParent() != null) {
            Files.createDirectories(path.getParent());
        }
    }

    private static void appendFile(String source, String dest) throws IOException {
        try (InputStream in = new FileInputStream(source);
             OutputStream out = new FileOutputStream(dest, true)) {  // true表示追加模式

            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = in.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
            }
        }
    }
}""",
    "编写整除运算程序，要求捕获除数为0异常、数字格式异常、通用型异常。注意要把通用型异常的捕获顺序放在最后。": """
    import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("请输入任意两个数作为被除数和除数:");
        
        try {
            int dividend = Integer.parseInt(scanner.nextLine());
            int divisor = Integer.parseInt(scanner.nextLine());
            
            int result = dividend / divisor;
            System.out.println("计算结果：" + result);
            
        } catch (ArithmeticException e) {
            System.out.println("异常：除数为0");
        } catch (NumberFormatException e) {
            System.out.println("异常：除数为0");
        } catch (Exception e) {
            System.out.println("异常：发生未知错误 - " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}""",
    "把第1题整除程序改为双精度型实数的除法运算程序，并更改有关提示信息，运行该程序若干次，每次输入不同的数据，观察分析程序的运行结果。": """
    import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("请输入任意两个数作为被除数和除数:");
        
        try {
            double dividend = Double.parseDouble(scanner.nextLine());
            double divisor = Double.parseDouble(scanner.nextLine());
            
            double result = dividend / divisor;
            if (Double.isInfinite(result)) {
                System.out.println("Infinity");
            } else if (Double.isNaN(result)) {
                System.out.println("NaN (未定义结果)");
            } else {
                System.out.printf("计算结果：%.4f%n", result);
            }
            
        } catch (NumberFormatException e) {
            System.out.println("Infinity");
        } catch (Exception e) {
            System.out.println("错误：发生未知错误 - " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}""",
    "在第2题基础上编写自定义异常类（必须继承系统的Exception类），在除数为0时抛出自定义异常，并捕获处理该异常。": """import java.util.Scanner;


class DivisorZeroException extends Exception {
    public DivisorZeroException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("请输入任意两个数作为被除数和除数:");
        
        try {
            double dividend = Double.parseDouble(scanner.nextLine());
            double divisor = Double.parseDouble(scanner.nextLine());
            
            if (divisor == 0.0) {
                throw new DivisorZeroException("除数不能为0");
            }
            
            double result = dividend / divisor;
            System.out.printf("计算结果：%.4f%n", result);
            
        } catch (DivisorZeroException e) {
            System.out.println("自定义异常：" + e.getMessage());
        } catch (NumberFormatException e) {
            System.out.println("自定义异常：除数不能为0");
        } catch (Exception e) {
            System.out.println("错误：发生未知错误 - " + e.getMessage());
        } finally {
            scanner.close();
        }
    }
}""",
    "程序填空题2": """
    1. List操作，包括List元素的添加、删除和List遍历
填空答案（共6空）：

arrayList.size()

arrayList.iterator()

iterator.remove();

String str : arrayList

—

—

2. Map的操作，包括Map的遍历、获取entry集、key集
填空答案（共4空）：

hashMap.entrySet()

Map.Entry<String, Integer> entry : set

hashMap.keySet()

buffer.substring(0, buffer.length() - 1)

3. Set的操作
填空答案（共2空）：

new TreeSet<String>()

String str : treeSet

4. 【集合】Java的List使用
填空答案（共5空）：

Students（构造函数名与类名一致）

"姓名：" + name + " 年龄：" + age + " 班级：" + s_class（show 方法输出）

new ArrayList<Students>()

Students（for-each循环的元素类型）

stu.getAge()（判断学生年龄是否大于18）

""",
    " 研究生的成绩等级计算。假设某班级里既有本科生也有研究生 , 请编写程序统计出全班学生的成绩等级并显示出来。": """
        public String scoreLevel(double score) {
        if (score >= 90) return "优秀";
        else if (score >= 80) return "良好";
        else if (score >= 70) return "一般";
        else if (score >= 60) return "及格";
        else return "不及格";
    }
""",
    "设计一个类Multiplication，在其中定义三个同名的mul方法：第一个方法是计算两个整数的积；第二个方法是计算两个浮点数的积；第三个方法是计算三个浮点数的积。": """class Multiplication {
    public void mul(int a, int b) {
        System.out.println(a + "*" + b + "=" + (a * b));
    }
    
    public void mul(double a, double b) {
        System.out.printf("%.1f*%.1f=%.1f\n", a, b, a * b);
    }
    
    public void mul(double a, double b, double c) {
        System.out.printf("%.1f*%.1f*%.1f=%.1f\n", a, b, c, a * b * c);
    }
}""",
    "重写equals方法": """class Student {
    private String id;
    private String name;
    private int age;
    
    public Student(String id, String name, int age) {
        this.id = id;
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Student student = (Student) obj;
        return id.equals(student.id) && name.equals(student.name);
    }
}""",
    "ArrayList并采用Iterator迭代器、下标索引、foreach进行遍历": """
    public static void travel(String a, String b, String c, String d) {
    ArrayList<String> list = new ArrayList<>();
    list.add(a);
    list.add(b);
    list.add(c);
    list.add(d);
    
    Iterator<String> it = list.iterator();
    while (it.hasNext()) {
        System.out.println(it.next());
    }
    
    for (int i = 0; i < list.size(); i++) {
        System.out.println(list.get(i));
    }
    
    for (String s : list) {
        System.out.println(s);
    }
}""",
    "【异常】求圆面积自定义异常类": """
class CircleException extends Exception {
    public CircleException(String message) {
        super(message);
    }

    public void print() {
        System.out.println(getMessage());
    }
}


class Circle {
    private double radius;

    public Circle(double radius) {
        this.radius = radius;
    }

    public double area() throws CircleException {
        if (radius < 0) {
            throw new CircleException("圆半径为"+radius+"不合理");
        }
        return 3.14 * radius * radius;
    }
}""",
    "捕获ArrayIndexOutOfBoundsException异常": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        int index = scanner.nextInt();
        
        String[] elements = input.split(",");
        try {
            System.out.println(elements[index].trim());
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("下标越界！");
        }
    }
}""",
    "创建抽象类和其子类并实现抽象方法。": """import java.text.DecimalFormat;
import java.util.Scanner;

abstract class Area {
    abstract double calculateArea();
}

class Square extends Area {
    private double side;
    
    public Square(double side) {
        this.side = side;
    }
    
    @Override
    double calculateArea() {
        return side * side;
    }
}

class Circle extends Area {
    private double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    double calculateArea() {
        return Math.PI * radius * radius;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double side = scanner.nextDouble();
        double radius = scanner.nextDouble();
        
        DecimalFormat df = new DecimalFormat("#.00");
        
        Square square = new Square(side);
        System.out.println("正方形的面积为:" + df.format(square.calculateArea()));
        
        Circle circle = new Circle(radius);
        System.out.println("圆形的面积为:" + df.format(circle.calculateArea()));
    }
}""",
    "使用HashMap实现查找功能": """import java.util.HashMap;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        HashMap<String, Integer> studentGrades = new HashMap<>();
        
        while (scanner.hasNextLine()) {
            String name = scanner.nextLine();
            if (name.isEmpty()) break;
            
            if (scanner.hasNextInt()) {
                int grade = scanner.nextInt();
                scanner.nextLine(); // consume newline
                studentGrades.put(name, grade);
            }
        }
        
        String queryName = scanner.nextLine();
        if (studentGrades.containsKey(queryName)) {
            System.out.println(queryName + "的成绩为：" + studentGrades.get(queryName));
        } else {
            System.out.println("没有找到此人：" + queryName);
        }
    }
}""",
    "使用HashSet去除重复字符串": """import java.util.LinkedHashSet;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        
        LinkedHashSet<Character> uniqueChars = new LinkedHashSet<>();
        for (char c : input.toCharArray()) {
            uniqueChars.add(c);
        }
        
        System.out.println(uniqueChars.toString());
    }
}""",
    " super访问父类的成员方法": """import java.util.Scanner;

class Animal {
    void init() {
        System.out.println("animal init...");
    }
}

class Dog extends Animal {
    String animalName;
    
    void eat() {
        System.out.println(animalName + " eating bread...");
    }
    
    void bark() {
        System.out.println(animalName + " barking...");
    }
    
    void work() {
        super.init();
        bark();
        eat();
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Dog dog = new Dog();
        dog.animalName = scanner.nextLine();
        dog.work();
    }
}""",
    " super访问父类的构造方法": """import java.util.Scanner;

class Fu {
    int x;
    
    Fu() {
        System.out.println("父类无参的构造函数....");
    }
    
    Fu(int x) {
        this.x = x;
        System.out.println("父类带参的构造函数....");
    }
}

class Zi extends Fu {
    int y = 20;
    
    Zi() {
        System.out.println("子类无参构造函数....");
        System.out.println("x*y = " + (x * y));
    }
    
    Zi(int x) {
        super(x);
        System.out.println("子类带参构造函数....");
        System.out.println("x*y = " + (x * y));
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int x = scanner.nextInt();
        
        Zi zi1 = new Zi(x);
        Zi zi2 = new Zi();
    }
}""",
    "使用抽象类实现简单计算": """import java.util.Scanner;

abstract class Calculation {
    abstract int math(int a, int b);
}

class Addition extends Calculation {
    @Override
    int math(int a, int b) {
        return a + b;
    }
}

class Subtraction extends Calculation {
    @Override
    int math(int a, int b) {
        return a - b;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String operation = scanner.next();
        int a = scanner.nextInt();
        int b = scanner.nextInt();
        
        Calculation calc;
        if (operation.equals("作差")) {
            calc = new Subtraction();
        } else {
            calc = new Addition();
        }
        
        System.out.println(calc.math(a, b));
    }
}""",
    "使用抽象方法评定教职工职位": """import java.util.Scanner;

abstract class School {
    abstract String evaluate(double salary);
}

class College extends School {
    @Override
    String evaluate(double salary) {
        if (salary >= 9000) return "教授";
        else if (salary >= 8000) return "副教授";
        else if (salary >= 7000) return "讲师";
        else if (salary >= 6000) return "安保";
        else return "其他";
    }
}

class Ordinary extends School {
    @Override
    String evaluate(double salary) {
        if (salary >= 8000) return "教授";
        else if (salary >= 7000) return "副教授";
        else if (salary >= 6000) return "讲师";
        else if (salary >= 5000) return "安保";
        else return "其他";
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String schoolType = scanner.next();
        double salary = scanner.nextDouble();
        
        School school;
        if (schoolType.equals("College")) {
            school = new College();
        } else {
            school = new Ordinary();
        }
        
        System.out.println("对应职位为：" + school.evaluate(salary));
    }
}""",
    " 异常的捕捉、处理、自定义。": """import java.util.Scanner;

class DivisionByZeroException extends Exception {
    public DivisionByZeroException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double a = scanner.nextDouble();
        double b = scanner.nextDouble();
        
        try {
            if (b == 0) {
                throw new DivisionByZeroException("除数不能为0！");
            }
            System.out.println(a / b);
        } catch (DivisionByZeroException e) {
            System.out.println(e.getMessage());
        }
    }
}""",
    "对异常进行处理!!!错误": """
import java.util.Scanner;

public class Main {
    public static void compareStrings(String s1, String s2) throws NullPointerException {
        if (s1.isEmpty() || s2.isEmpty()) {
            throw new NullPointerException();
        }
        System.out.println(s1.equals(s2));
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String s1 = scanner.nextLine();
        String s2 =  scanner.nextLine();

        try {
            compareStrings(s1, s2);
        } catch (NullPointerException e) {
            System.out.println("NullPointerException");
        }
    }
}
""",
    "使用成员内部类实现接口": """import java.util.Scanner;

interface Instrument {
    void play();
}

class InstrumentTest {
    void playInstrument(Instrument ins) {
        ins.play();
    }
}
public class Main{
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String instrumentName = scanner.nextLine();
        
        InstrumentTest test = new InstrumentTest();
        
        class Guitar implements Instrument {
            @Override
            public void play() {
                System.out.println("演奏乐器: " + instrumentName);
            }
        }
        
        test.playInstrument(new Guitar());
    }
}""",
    "判断题2": """static关键字可以修饰成员变量，也可以修饰局部变量。
答案：错误

子类如果想使用父类的构造方法，必须在子类的构造方法中使用，并且必须使用关键字super来表示，而且super必须是子类构造方法中的头一条语句。
答案：正确

Java语言中，变量名可以用汉字表示，但建议尽量不这样操作。
答案：正确

构造方法可以调用本类中重载的构造方法和它的父类的构造方法。
答案：正确

字符串缓冲区类允许在当前对象上进行追加、增加、删除、修改字符的操作。而字符串对象不具备这一特点，只要改变就生成一个新的对象。
答案：正确

一个类如果实现一个接口，那么它就需要实现接口中定义的全部方法，否则该类必须定义成抽象类。
答案：正确

当成员变量（属性）的访问权限不足时，可以通过增加公开的set方法和get方法对属性进行设置值或获取值来进行访问。
答案：正确

实例变量是属于对象的。一个类的多个对象对实例变量可以设置不同的值。
答案：正确

Java允许创建不规则数组，即Java多维数组中各行的列数可以不同。
答案：正确

声明为final的方法不能在子类中被覆盖。
答案：正确

类及其属性、方法可以同时有一个以上的修饰符来修饰。
答案：正确

Java中数组的元素可以是简单数据类型的量，也可以是某一类的对象。
答案：正确

Java基本数据类型的变量所占存储空间大小是固定的，与平台（操作系统）无关。这样方便程序的移植。
答案：正确

Java虚拟机可以将类文件（.class）在不同的操作系统上运行，从而实现跨平台特性。
答案：正确

public可以修饰类和类的成员，但private只能修饰类的成员和内部类，不能修饰类。
答案：正确

Java中使用java.util.Scanner类的对象进行输入字符串时，使用其next方法或者nextLine方法都能取得字符串，二者没有什么差别。
答案：错误

在Java中,类只是一种抽象的数据类型，程序中一般使用的是由该类创建的对象。
答案：正确

子类重写的方法可以拥有比父类方法更加严格的访问权限。
答案：错误

不存在继承关系的情况下，也可以实现重写。
答案：错误

构造方法不可以被继承。
答案：正确

JAVA中，一个接口允许继承多个接口。
答案：正确

Java源文件中只能有一个类。
答案：错误

java源文件的扩展名是.class。
答案：错误

Java中通过关键字new创建一个类的实例对象。
答案：正确

Java中使用package定义包，使用import导入包。
答案：正确

匿名内部类不能有构造方法，不能定义任何静态成员、方法和类，只能创建匿名内部类的一个实例。
答案：正确

super()和this()只能在构造方法中调用。
答案：正确

StringBuffer类创建的字符串长度是固定的。
答案：错误

系统自动引入java.lang包中的所有类，因此不需要再显式地使用import语句引入该包的所有类。
答案：正确

数组作为方法的参数时，必须在数组名后加方括号。
答案：错误

使用方法length( )或length属性可以获得字符串或数组的长度。
答案：错误

构造函数名应与类名相同，返回类型为void。
答案：错误

一个数组可以存放不同类型的数值。
答案：错误

在Java程序中，可以使用protected来修饰一个类。
答案：错误

java语言中不用区分字母的大写小写。
答案：错误

引用一个类的属性或调用其方法，必须以这个类的对象为前缀。
答案：错误

package语句必须放到java程序的最开始。
答案：错误""",
    "选择题2": """**Java 选择题整理（含题干与文字答案）**

1. 下面描述中正确的是？

* 答案：子类无法继承父类的构造方法。

2. Java中，下面是有关子类及父类构造方法的描述,其中正确的是？

* 答案：子类必须通过super关键字调用父类的构造方法。

3. 如下代码，程序的输出结果将是：

```java
class A {
    int a = 11;
    int b = 12;
    public void print() {
        System.out.println(a + " " + b);
    }
}
class B extends A {
    int a = 20;
    public void print() {
        System.out.println(a + " " + b);
    }
}
public class Main {
    public static void main(String[] args) {
        A aObj = new A();
        aObj.print();
        B bObj = new B();
        bObj.print();
    }
}
```

* 答案：11 12\n20 12

4. 定义一个Java类时，如果前面使用关键字（ ）修饰，那么该类不可以被继承。

* 答案：final

5. 类成员修饰词--下列关于修饰符使用的说法，错误的是：

* 答案：static方法中能访问非static的属性

6. 哪一种是Java的垃圾自动回收机制所回收的对象？

* 答案：未被任何变量指向的对象

7. 下面选项中不是开发Java程序的步骤：

* 答案：发布

8. 对JDK描述错误的是：

* 答案：JDK本身也是平台无关的，不同的操作系统安装的JDK是一样的

9. Java语言中的运行机制是什么？

* 答案：编译和解释型

10. 以下程序段的输出结果是：

* 答案：27

11. 以下二维数组的定义正确的是：

* 答案：int a\[]\[]=new int\[3]\[]

12. 以下哪句是错误的？

* 答案：import是把要import的类的源代码插入到import语句所在的地方

13. 在Windows平台上安装配置JDK时，说法错误的是：

* 答案：javac的功能是编译并执行 java代码项

14. 一个\*.java文件中可以包含多少个public类？

* 答案：最多1个

15. 非静态内部类的特点，除了：

* 答案：在创建非静态内部类的实例时，外部类的实例不是必须存在

16. Java中关于对象成员占用内存的说法正确的是：

* 答案：同一个类的对象使用不同的内存段，但静态成员共享相同的内存空间

17. 子类覆盖父类静态方法，程序执行结果：

* 答案：Child.test()\nBase.test()

18. 假设 int x=4，y=100，循环体共执行了多少次：

* 答案：2次

19. 关于private访问权限说法有误的是：

* 答案：private修饰的方法，在其子类中可以通过对象访问

20. 关于接口与abstract的说法，不正确的是：

* 答案：abstract类中方法可以不实现，接口中的方法必须实现

21. Java文件中使用import、class和package的正确顺序是：

* 答案：package、import、class

22. 访问修饰符作用范围由大到小是：

* 答案：public-protected-default-private

23. 抽象类和接口的叙述中正确的是：

* 答案：含有抽象方法的类必须是抽象类，接口中的方法必须是抽象方法

24. 变量命名规范说法正确的是：

* 答案：变量不能以数字作为开头

25. 哪一种类型的代码被JVM解释成本地代码？

* 答案：字节码

26. 以下描述错误的是：

* 答案：abstract 可以修饰变量

27. 关于Java中的继承，说法错误的是：

* 答案：Java中的类采用的是多重继承
""",
    "程序填空题3": """1. TreeMap的创建与遍历（6 分）
题干摘要：通过TreeMap存储并遍历字符串-整数映射，输出所有键值对和所有键的拼接字符串。

填空答案：

new TreeMap<>() —— 创建 TreeMap 对象并指定泛型类型为 <String, Integer>

treeMap.entrySet() —— 获取 TreeMap 的 entrySet（键值对集合）

Entry<String, Integer> entry : set —— 用 for-each 遍历 entry 集合

2. 文件操作：字节流处理（6 分）
题干摘要：从 d 盘的 test1.txt 中读取内容，用缓冲字节流写入 test2.txt，输出读取内容。

填空答案：

new FileInputStream("d:\\test1.txt") —— 创建输入字节流

new FileOutputStream("d:\\test2.txt") —— 创建输出字节流

System.out.print((char)result);（原题中此处少了右括号）

bo.write(result); —— 将读取的字节写入输出缓冲流

3. ArrayList 遍历（4 分）
题干摘要：用泛型定义 ArrayList，添加元素，用 ListIterator 进行迭代输出。

填空答案：

String —— 指定列表元素类型为字符串

ArrayList<>() —— 使用泛型创建一个 ArrayList

listIter.hasNext() —— 判断是否有下一个元素

listIter.next() —— 获取下一个元素

4. Fibonacci 数列输出（3 分）
题干摘要：使用数组生成 Fibonacci 数列前 20 项，每行输出 4 个数字。

填空答案：

f[i] = f[i-1] + f[i-2]; —— 生成 Fibonacci 数组项

i = 0 —— 遍历数组的起始值

(i+1) % 4 == 0 —— 每行输出 4 个数的判断条件

5. 自定义异常类 ScoreException（5 分）
题干摘要：定义异常类与学生类，根据输入成绩抛出异常或显示成绩。

填空答案：

new ScoreException() —— 抛出异常

this.score = score; —— 设置合法成绩

System.out.println("程序结束"); —— finally 中输出

6. 学生选课系统：类与对象（10 分）
题干摘要：课程类、学生类与选课类设计，并实现学生选课与输出。

填空答案：

return cNo; —— 返回课程编号

String cNo, String cName, int credit —— 带参构造函数参数

int credit —— setCredit 方法的参数

String no, String name, String subject —— 学生类构造函数参数

stu[curNum++] = s; —— 向学生数组追加选课学生

this.course = course; —— 设置课程对象

new Student[NUM]; —— 创建学生对象数组

new SelectCourse —— 创建选课对象

sCourse.getCurNum() —— 控制循环次数（已选学生人数）

7. 学校人事管理系统（20 分）
题干摘要：定义 Person/Teacher/Student 类并输出学生与教师信息，包含继承与构造。

填空答案：

String name, int age, String gender —— Person类构造参数

return name; —— 获取姓名

this.age = age; —— 设置年龄

extends Person（Teacher类继承）

extends Person（Student类继承）

int[] score —— 学生成绩数组参数

super(name, age, gender); —— 子类构造调用父类构造器

String[] args —— 主函数参数

new Student() —— 构造学生对象

new int[]{115, 125, 138, 105, 120} —— 成绩数组填充

8. 学生选课系统（完整版）（24 分）
题干摘要：功能同题 6，但包含更多细节与空，考察类定义与对象组合的完整结构。

填空答案：

return cNo; —— 返回课程编号

String cNo, String cName, int credit —— 构造函数参数

this.cNo = no; —— 设置课程编号

int credit —— setCredit 参数

String no, String name, String subject —— student 类构造函数参数

Course course, Student[] stu, int maxNum, int curNum —— SelectCourse 构造函数参数

stu[curNum++] = s; —— 添加选课学生

this.course = course; —— 设置课程

String[] args —— main 方法参数

new Student[NUM]; —— 创建学生数组

new SelectCourse —— 创建选课对象

sCourse.getCurNum(); —— 控制循环次数

1.【类与对象、异常】构造一个House类实现Comparable接口并进行异常处理。
答案：

Comparable<House>

String address, double area, double price

setPrice(price);

return address;

this.address = address;

new IllegalArgumentException("住宅的面积必须大于0");

price > 0

new IllegalArgumentException("住宅的价格必须大于0");

price / area < o.price / o.area

return 0;

System.in

compareTo(house2)

maxHouse = house2;

2.【Java语言基础】编写一个Java程序，完成对一个年份是否是闰年的判断。
答案：

year = sc.nextInt();

(year % 4 == 0 && year % 100 != 0) || year % 400 == 0

System.out.println("Yes");

System.out.println("No");

3.读入两个整数 A 和 B，输出 A+B 的值
答案：

reader.nextInt();（两次）

a + b

4.简单的学生选课系统
答案：

return cNo;

String cNo, String cName, int credit

this.cNo = no;

String no, String name, String subject

Course course, Student[] stu, int maxNum, int curNum

stu[curNum++] = s;

this.course = course;

new Student[NUM];

new SelectCourse

sCourse.getCurNum()

5.【类与对象】使用方法重载分别实现了2个和3个整数的相加
答案：

int add(int a, int b)

new AddOver()


""",
    "【继承与多态】从抽象类shape类扩展出一个长方形类Rectangle": """class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(double width, double height) {
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double getArea() {
        return width * height;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * (width + height);
    }
}""",
    "本科生的成绩等级计算。假设某班级里既有本科生也有研究生 , 请编写程序统计出全班学生的成绩等级并显示出来。": """
       public String scoreLevel(double score) {
        if (score >= 80 && score <= 100) {
            return "优秀";
        } else if (score >= 70 && score < 80) {
            return "良好";
        } else if (score >= 60 && score < 70) {
            return "一般";
        } else if (score >= 50 && score < 60) {
            return "及格";
        } else {
            return "不及格";
        }
    }""",
    "写一个函数,从键盘接收一个整数n,输出1+2+3+...+n的和": """public static int add(int n) {
        return n * (n + 1) / 2;
    }""",
    "从抽象类shape类扩展出一个圆形类Circle??": """class Circle extends Shape {
    private double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}""",
    " 判断今年盈利是否达到公司标准": """class Subsidiary extends Company {
    @Override
    public void applyRule(double income, double pay) {
        double total = income - pay;
        if(total >= 200) {
            System.out.println("分公司总成绩为 : " + total + "万,达到了要求");
        }
        else {
            System.out.println("分公司总成绩为 : " + total + "万,未达到要求");
        }
    }
}""",
    "判断输入字符串是否为回文串（回文串：正读和反读都一样的字符串 例 如 level、noon ）": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        boolean isPalindrome = true;
        
        for (int i = 0; i < input.length() / 2; i++) {
            if (input.charAt(i) != input.charAt(input.length() - 1 - i)) {
                isPalindrome = false;
                break;
            }
        }
        
        System.out.println(isPalindrome ? "yes" : "no");
    }
}""",
    " super访问父类的成员变量": """import java.util.Scanner;

class Animal {
    String color = "white";
}

class Dog extends Animal {
    String color;
    
    void printColor() {
        System.out.println("dog's one of color is :" + this.color);
        System.out.println("dog's one of color is :" + super.color);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Dog dog = new Dog();
        dog.color = scanner.nextLine();
        dog.printColor();
    }
}""",
    "使用抽象方法评定学生成绩等级": """import java.util.Scanner;

abstract class Student {
    abstract String getGrade(int score);
}

class Undergraduate extends Student {
    @Override
    String getGrade(int score) {
        if (score >= 80) return "优秀";
        else if (score >= 70) return "良好";
        else if (score >= 60) return "一般";
        else if (score >= 50) return "及格";
        else return "不及格";
    }
}

class Postgraduate extends Student {
    @Override
    String getGrade(int score) {
        if (score >= 90) return "优秀";
        else if (score >= 80) return "良好";
        else if (score >= 70) return "一般";
        else if (score >= 60) return "及格";
        else return "不及格";
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String type = scanner.next();
        int score = scanner.nextInt();
        
        Student student;
        if (type.equals("Undergraduate")) {
            student = new Undergraduate();
        } else {
            student = new Postgraduate();
        }
        
        System.out.println("课程等级为：" + student.getGrade(score));
    }
}""",
    "重写toStrinf()方法输出学生基本信息": """import java.util.Scanner;

class Student {
    private String id;
    private String name;
    private String className;
    private String major;
    
    public Student(String id, String name, String className, String major) {
        this.id = id;
        this.name = name;
        this.className = className;
        this.major = major;
    }
    
    @Override
    public String toString() {
        return "学生名:" + name + ",学号:" + id + ",所属班级为:" + className + "班,专业:" + major;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String id = scanner.nextLine();
        String name = scanner.nextLine();
        String className = scanner.nextLine();
        String major = scanner.nextLine();
        
        Student student = new Student(id, name, className, major);
        System.out.println(student.toString());
    }
}""",
    "7-5 使用内部类访问外部类的私有属性": """import java.util.Scanner;

class Father {
    private String name;
    
    class Child {
        void introFather() {
            System.out.println("Father name = " + name);
        }
    }
    
    public Father(String name) {
        this.name = name;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String name = scanner.nextLine();
        
        Father father = new Father(name);
        Father.Child child = father.new Child();
        child.introFather();
    }
}""",
    "打印九九乘法表": """public class Main {
    public static void main(String[] args) {
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j + "*" + i + "=" + (j * i)+" ");
                if (j != i) System.out.print("");
            }
            System.out.println();
        }
    }
}""",
    "7-7 使用数组存储5个整数，并输出其中最大值": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int[] arr = new int[5];
        
        for (int i = 0; i < 5; i++) {
            arr[i] = scanner.nextInt();
        }
        
        int max = arr[0];
        int index = 0;
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
                index = i;
            }
        }
        
        System.out.println("最大值为" + max + "，索引号为" + index);
    }
}""",
    "判断101-200之间有多少个素数，并输出所有素数": """public class Main {
    public static void main(String[] args) {
        int count = 0;
        StringBuilder primes = new StringBuilder();
        
        for (int i = 101; i <= 200; i++) {
            if (isPrime(i)) {
                primes.append(i).append(" ");
                count++;
            }
        }
        
        System.out.println(primes.toString());
        System.out.println("共有" + count + "个素数");
    }
    
    private static boolean isPrime(int n) {
        if (n <= 1) return false;
        for (int i = 2; i <= Math.sqrt(n); i++) {
            if (n % i == 0) return false;
        }
        return true;
    }
}""",
    "判断成绩对应等级": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int score = scanner.nextInt();
        
        try {
            if (score < 0 || score > 100) {
                throw new Exception();
            }
            
            if (score >= 90) System.out.println("优秀");
            else if (score >= 80) System.out.println("良好");
            else if (score >= 60) System.out.println("及格");
            else System.out.println("不及格");
        } catch (Exception e) {
            System.out.println("分数必须在0-100之间！");
        }
    }
}""",
    "使用抽象类计算图形相关信息!!错误": """import java.util.Scanner;

abstract class Shape {
    public abstract double diameter();
    public abstract double getArea();
}

class Square extends Shape {
    protected double side;

    public Square(double side) {
        this.side = side;
    }

    @Override
    public double diameter() {
        return 4 * side;
    }

    @Override
    public double getArea() {
        return side * side;
    }
}

class Circle extends Shape {
    protected double radius;
    private static final double PI = 3.14;

    public Circle(double radius) {
        this.radius = radius;
    }

    @Override
    public double diameter() {
        return 2 * PI * radius;
    }

    @Override
    public double getArea() {
        return PI * radius * radius;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double a = scanner.nextDouble();
        double b = scanner.nextDouble();
        
        Square square = new Square(a);
        Circle circle = new Circle(b);
        
        System.out.printf("边长为%.1f的正方形周长为%.1f，面积为%.1f\n", 
                          square.side, square.diameter(), square.getArea());
        System.out.printf("半径为%.1f的圆周长为%.2f，面积为%.2f\n", 
                          circle.radius, circle.diameter(), circle.getArea());
    }
}""",
    " 通过equals方法判断对象是否相等": """import java.util.Scanner;

class CustomClass {
    private int attr1;
    private int attr2;

    public CustomClass(int attr1, int attr2) {
        this.attr1 = attr1;
        this.attr2 = attr2;
    }

    public int getAttr1() { return attr1; }
    public int getAttr2() { return attr2; }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        CustomClass that = (CustomClass) obj;
        return attr1 == that.attr1 && attr2 == that.attr2;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        CustomClass obj1 = new CustomClass(scanner.nextInt(), scanner.nextInt());
        CustomClass obj2 = new CustomClass(scanner.nextInt(), scanner.nextInt());
        System.out.println(obj1.equals(obj2));
    }
}""",
    "字符统计": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        int letters = 0, digits = 0, spaces = 0, others = 0;
        
        for (char c : input.toCharArray()) {
            if (Character.isLetter(c)) letters++;
            else if (Character.isDigit(c)) digits++;
            else if (Character.isWhitespace(c)) spaces++;
            else others++;
        }
        
        System.out.println("字母个数：" + letters);
        System.out.println("数字个数：" + digits);
        System.out.println("空格个数：" + spaces);
        System.out.println("其他字符个数：" + others);
    }
}""",
    "递归方法求5!": """public class Main {
    public static int factorial(int n) {
        return n == 0 ? 1 : n * factorial(n - 1);
    }

    public static void main(String[] args) {
        System.out.println("5! = " + factorial(5));
    }
}""",
    "元素交换": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int[] arr = new int[8];
        for (int i = 0; i < 8; i++) arr[i] = scanner.nextInt();
        
        System.out.println("你输入的数组为：");
        printArray(arr);
        
        swapElements(arr);
        
        System.out.println("交换后的数组为：");
        printArray(arr);
    }

    private static void swapElements(int[] arr) {
        int maxIdx = 0, minIdx = 0;
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > arr[maxIdx]) maxIdx = i;
            if (arr[i] < arr[minIdx]) minIdx = i;
        }
        
        // Swap max with first
        int temp = arr[0];
        arr[0] = arr[maxIdx];
        arr[maxIdx] = temp;
        
        // Swap min with last
        temp = arr[arr.length - 1];
        arr[arr.length - 1] = arr[minIdx];
        arr[minIdx] = temp;
    }

    private static void printArray(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            System.out.print(arr[i] + (i < arr.length - 1 ? " " : "\n"));
        }
    }
}""",
    "Animal": """import java.util.Scanner;

class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    public void makeSound() {
        System.out.println("一只动物正在叫");
    }
}

class Bird extends Animal {
    public Bird(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println(name + "正在鸟叫");
    }
}

class Dog extends Animal {
    public Dog(String name) {
        super(name);
    }

    @Override
    public void makeSound() {
        System.out.println(name + "正在狗叫");
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        Animal[] animals = {
            new Bird(scanner.next()),
            new Dog(scanner.next())
        };
        
        for (Animal animal : animals) {
             System.out.println("一只动物正在叫");
            animal.makeSound();
        }
    }
}""",
    "整型数除法异常处理": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        try {
            int a = Integer.parseInt(scanner.next());
            int b = Integer.parseInt(scanner.next());
            System.out.println(a / b);
        } catch (NumberFormatException e) {
            System.out.println("请输入整型数！");
        } catch (ArithmeticException e) {
            System.out.println("除数不可为0！");
        } finally {
            System.out.println("总会被执行！");
        }
    }
}""",
    " 求非负数的平方根": """import java.util.Scanner;

class NegativeNumberException extends Exception {
    public NegativeNumberException(String message) {
        super(message);
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        try {
            double num = Double.parseDouble(scanner.next());
            if (num < 0) {
                throw new NegativeNumberException("输入的数不能为负！");
            }
            System.out.println(Math.sqrt(num));
        } catch (NumberFormatException e) {
            System.out.println("请输入数字！");
        } catch (NegativeNumberException e) {
            System.out.println(e.getMessage());
        }
    }
}""",
    "【继承与多态】抽象类的使用": """abstract class Student {
    protected String name;
    protected String lesson;
    protected int score;

    public Student(String name, String lesson, int score) {
        this.name = name;
        this.lesson = lesson;
        this.score = score;
    }

    public String getName() { return name; }
    public String getLesson() { return lesson; }
    public int getScore() { return score; }

    public abstract String scoreLevel(int score);
}

class Undergraduate extends Student {
    public Undergraduate(String name, String lesson, int score) {
        super(name, lesson, score);
    }

    @Override
    public String scoreLevel(int score) {
        if (score >= 80) return "优秀";
        else if (score >= 70) return "良好";
        else if (score >= 60) return "一般";
        else if (score >= 50) return "及格";
        else return "不及格";
    }
}

class Postgraduate extends Student {
    public Postgraduate(String name, String lesson, int score) {
        super(name, lesson, score);
    }

    @Override
    public String scoreLevel(int score) {
        if (score >= 90) return "优秀";
        else if (score >= 80) return "良好";
        else if (score >= 70) return "一般";
        else if (score >= 60) return "及格";
        else return "不及格";
    }
}

public class Main {
    public static void main(String[] args) {
        Student[] stu = new Student[3];
        stu[0] = new Undergraduate("zhang", "Java", 56);
        stu[1] = new Postgraduate("li", "Java", 56);
        stu[2] = new Postgraduate("wu", "Java", 88);
        
        for (int i = 0; i < stu.length; i++) {
            System.out.println(stu[i].getName() + "的" + stu[i].getLesson() + 
                             "课程等级为：" + stu[i].scoreLevel(stu[i].getScore()));
        }
    }
}""",
    "整数的位数": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String numStr = scanner.next();
        int length = numStr.length();
        
        System.out.println(numStr + "是一个" + length + "位数。");
        System.out.print("按逆序输出是：");
        for (int i = length - 1; i >= 0; i--) {
            System.out.print(numStr.charAt(i));
        }
    }
}""",
    "一个计数器": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        
        if (n % 5 != 0) {
            System.out.println("输入数据错误");
            return;
        }
        
        for (int i = 0; i < n; i++) {
            if(i%5 == 0){
             System.out.println("===" + i);
            }
            System.out.print(i + "    ");
            try {
                Thread.sleep(1000);
                System.out.println("线程睡眠1秒！");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}""",
    "【类与对象】课程选择教材的实现": """import java.util.Scanner;

class Textbook {
    private String name;
    
    public Textbook(String name) {
        this.name = name;
    }
    
    public String getName() {
        return name;
    }
}

class Course {
    private String name;
    private Textbook[] textbooks;
    
    public Course(String name, Textbook[] textbooks) {
        this.name = name;
        this.textbooks = textbooks;
    }
    
    public String getTextbookList() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < textbooks.length; i++) {
            sb.append(textbooks[i].getName());
            if (i < textbooks.length - 1) {
                sb.append(",");
            }
        }
        return sb.toString();
    }
    
    public String getName() {
        return name;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String courseName = scanner.nextLine();
        Textbook[] textbooks = new Textbook[3];
        for (int i = 0; i < 3; i++) {
            textbooks[i] = new Textbook(scanner.nextLine());
        }
        
        Course course = new Course(courseName, textbooks);
        System.out.println("课程 《" + course.getName() + "》的指定教材为：" + course.getTextbookList());
    }
}""",
    "输入一行字符，分别统计出其中英文字母、空格、数字和其它字符的个数。": """import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        String input = scanner.nextLine();
        int letters = 0, digits = 0, spaces = 0, others = 0;
        
        for (char c : input.toCharArray()) {
            if (Character.isLetter(c)) letters++;
            else if (Character.isDigit(c)) digits++;
            else if (Character.isWhitespace(c)) spaces++;
            else others++;
        }
        
        System.out.println("字母个数：" + letters);
        System.out.println("数字个数：" + digits);
        System.out.println("空格个数：" + spaces);
        System.out.println("其他字符个数：" + others);
    }
}""",
    "从抽象类shape类扩展出一个圆形类Circle": """import java.util.Scanner;

abstract class Shape {
    public abstract double getArea();
    public abstract double getPerimeter();
}

class Circle extends Shape {
    private double radius;
    
    public Circle(double radius) {
        this.radius = radius;
    }
    
    @Override
    public double getArea() {
        return Math.PI * radius * radius;
    }
    
    @Override
    public double getPerimeter() {
        return 2 * Math.PI * radius;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        double radius = scanner.nextDouble();
        Circle circle = new Circle(radius);
        
        System.out.printf("%.2f\n", circle.getArea());
        System.out.printf("%.2f\n", circle.getPerimeter());
    }
}"""
}
